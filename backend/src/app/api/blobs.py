"""Blob upload and download (`07` §5.1, FR-421).

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/blobs/upload-url` | Presigned upload so large files bypass the API process |
| `POST` | `/blobs/uploads/{id}/complete` | Complete a Blob Upload: a `blob.promote` Job (FR 8058) |
| `GET` | `/blobs/{sha256}` | Download, permission-checked, as a presigned redirect |

Declared by `07` §5.1 and reassigned to WK-660 by the endpoint audit: a dataset version's
parquet tables are blobs, so "download this version's data" needs them.

**Download is a 307 to a short-lived presigned URL, not a proxy.** A parquet table is
hundreds of megabytes and streaming it through the API process would tie up a worker for
the length of a download — a handful of concurrent downloads is then an outage. The
permission check happens here; the bytes never touch this process.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Response, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select

from app.api.authz import requires
from app.api.deps import Caller, job_identity
from app.api.responses import problems
from app.db.models import BlobRow, BlobUploadRow, JobRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import jobs as job_service
from app.platform.blobs import (
    UPLOAD_COMPLETE_WITHIN,
    BlobStore,
    blob_not_found,
    blob_readable_by,
    to_ref,
)
from model_schema import Job, JobKind, new_uuid7
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

    id: UUID
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
    body: UploadUrlRequest, caller: WriteDatasets, database: DatabaseDep, blob_store: BlobStoreDep
) -> UploadUrlResponse:
    """FR-421.

    The digest is not known until the bytes exist, so the object lands on a staging key, not
    at its content address. Asking the client for the digest up front would let it choose
    one, which is the difference between content addressing and client-supplied naming.
    The request records a Blob Upload in the caller's workspace and returns its `id`;
    `POST /blobs/uploads/{id}/complete` moves the staged object to its content address and
    records its owner (FR 8058).
    """
    presigned = await blob_store.presign_upload(body.media_type, body.parts)
    created = datetime.now(UTC)
    upload = BlobUploadRow(
        id=new_uuid7(),
        workspace_id=caller.workspace_id,
        principal_id=caller.principal.id,
        staging_key=presigned.key,
        s3_upload_id=presigned.upload_id,
        part_count=body.parts,
        media_type=body.media_type,
        created_at=created,
        complete_by=created + UPLOAD_COMPLETE_WITHIN,
    )
    async with database.unit_of_work() as session:
        session.add(upload)
    return UploadUrlResponse(
        id=upload.id,
        key=presigned.key,
        upload_id=presigned.upload_id,
        urls=list(presigned.urls),
        expires_in_s=presigned.expires_in_s,
    )


@router.post(
    "/uploads/{upload_id}/complete",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Complete a Blob Upload",
    responses=problems(401, 403, 404, 409, 422),
)
async def complete_upload(
    upload_id: UUID, caller: WriteDatasets, database: DatabaseDep, response: Response
) -> Job:
    """**202** with the `blob.promote` Job (FR 8058, `07` R1).

    Reads the Blob Upload only; the Job does the S3 work, so no upload byte crosses this
    process. Another workspace's Blob Upload is the same `404` as a missing one. A repeat
    returns the first Job, whatever its state: the row is locked while the Job is created, so
    two concurrent completions cannot make two.
    """
    async with database.unit_of_work() as session:
        upload = await session.get(BlobUploadRow, upload_id, with_for_update=True)
        if upload is None or upload.workspace_id != caller.workspace_id:
            raise PlatformError(
                "NOT_FOUND", "Blob Upload not found", 404, f"No Blob Upload {upload_id}."
            )
        if upload.job_id is not None:
            existing = await session.get(JobRow, upload.job_id)
            assert existing is not None
            job = job_service.to_schema(existing)
        else:
            if datetime.now(UTC) > upload.complete_by:
                raise PlatformError(
                    "VALIDATION_FAILED",
                    "The Blob Upload's completion deadline has passed",
                    409,
                    f"Blob Upload {upload_id} had to be completed by {upload.complete_by:%c}.",
                )
            job = await job_service.submit(
                session,
                JobKind.BLOB_PROMOTE,
                {**job_identity(caller), "upload_id": str(upload_id)},
                caller.principal,
                workspace_id=caller.workspace_id,
            )
            upload.job_id = job.id
    response.headers["Location"] = f"/api/v1/jobs/{job.id}"
    return job


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
        readable = row is not None and await blob_readable_by(
            session, sha256=sha256, workspace_id=caller.workspace_id
        )
    if not readable:
        raise blob_not_found(sha256)
    assert row is not None

    url = await blob_store.presign_download(
        to_ref(row),
        expires_in_s=expires_in_s,
    )
    # 307 rather than 302: the method must be preserved, and a client following a 302 with
    # a rewritten method would send GET where it meant GET but need not have.
    return RedirectResponse(url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
