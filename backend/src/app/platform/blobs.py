"""The content-addressed blob store (FR-418, FR-419, FR-420, FR-421, ID-4).

Two stores, one object. The **body** lives in S3 at `blob/{sha256[:2]}/{sha256}`; the
**size, media type and reference count** live in PostgreSQL, because a reference count is
a transactional quantity and S3 has no transactions.

The write order is deliberate and not symmetric:

    upload to S3  →  then insert the row

A crash between the two leaves an object with no row: an orphan, which GC reclaims. The
reverse order leaves a row with no object — a reference that resolves to nothing, which no
sweep can repair and which surfaces months later when someone opens a dataset. Orphaned
bytes are cheap; dangling references are not.

Content addressing makes the upload safely repeatable: the same content produces the same
key and the same bytes, so a retried upload is indistinguishable from the first.

boto3 is synchronous. Its calls are run through `asyncio.to_thread` rather than pulling in
a second AWS client library — a blocking S3 call on the event loop stalls every other
request on the process, and the symptom is latency under concurrency rather than an error.
"""

from __future__ import annotations

import asyncio
import hashlib
from collections.abc import AsyncIterator, Iterable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any, Final, cast
from uuid import UUID

import boto3
from botocore.client import Config as BotoConfig
from botocore.exceptions import BotoCoreError, ClientError
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import CursorResult, select, text, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.db.models import (
    BlobRow,
    BlobUploadRow,
    DatasetVersionRow,
    JobRow,
    RegressionRunRow,
    ScoringTraceRow,
)
from app.errors import PlatformError
from app.observability.logging import get_logger
from app.platform import audit
from model_schema import BlobRef, JobSource, Principal, new_uuid7

if TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_s3.client import S3Client
    from mypy_boto3_s3.type_defs import PartTypeDef

    from app.db.session import Database

__all__ = [
    "BLOB_OWNERS",
    "GC_FUNCTION_STATEMENTS",
    "GC_LOCK_TIMEOUT_S",
    "INSIDE_BLOB_OWNERS",
    "OWNER_WRITERS",
    "QUOTE_INPUT_BLOB_COLUMNS",
    "STAGING_EXPIRY_DAYS",
    "UPLOAD_COMPLETE_WITHIN",
    "BlobOwner",
    "BlobStore",
    "GarbageCollectionReport",
    "OwnerWriter",
    "PresignedUpload",
    "blob_key",
    "blob_not_found",
    "blob_probe",
    "blob_readable_by",
    "owner_count",
    "render_gc_function_statements",
    "to_ref",
]

_log = get_logger("app.blobs")

_CHUNK_SIZE: Final = 1024 * 1024  # 1 MiB

#: `RL-1724` DP-U1.2. Staged bytes and incomplete multipart uploads older than this are removed
#: by a lifecycle rule on `staging/`. The completion deadline (24 h, `UPLOAD_COMPLETE_WITHIN`)
#: must stay shorter than this, whatever the store does.
STAGING_EXPIRY_DAYS: Final = 2
UPLOAD_COMPLETE_WITHIN: Final = timedelta(hours=24)
_STAGING_RULE_ID: Final = "expire-staging"  # the bucket lifecycle rule this module owns


def blob_key(sha256: str) -> str:
    """`blob/{sha256[:2]}/{sha256}` (FR-418).

    The two-character prefix exists because some object stores and every filesystem-backed
    one degrade badly with millions of siblings in a single directory. It is derived, never
    stored: two places holding the same path is two places to disagree.
    """
    return f"blob/{sha256[:2]}/{sha256}"


class PresignedUpload(BaseModel):
    """A presigned URL set for a large upload (FR-421)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    upload_id: str | None = Field(
        default=None, description="S3 multipart upload id; null for a single-part upload."
    )
    key: str
    urls: tuple[str, ...] = Field(description="One presigned URL per part, in order.")
    expires_in_s: int


class GarbageCollectionReport(BaseModel):
    """What a GC run did, or would do when `dry_run` (FR-420)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    dry_run: bool
    grace_days: int
    considered: int
    deleted: tuple[str, ...] = ()
    bytes_reclaimed: int = 0
    #: Digests whose row was deleted but whose object was kept because a `put` re-created the
    #: row before the object step. Set on the returned report only, after the audit event.
    re_put: tuple[str, ...] = ()


class BlobStore:
    """S3-backed blob storage with PostgreSQL-side accounting."""

    def __init__(self, settings: Settings) -> None:
        self._bucket = settings.blob_bucket
        self._settings = settings
        self._client: S3Client = boto3.client(
            "s3",
            endpoint_url=settings.blob_endpoint_url,
            aws_access_key_id=settings.blob_access_key.get_secret_value(),
            aws_secret_access_key=settings.blob_secret_key.get_secret_value(),
            region_name=settings.blob_region,
            # Path addressing: MinIO does not serve virtual-host style buckets by default,
            # and the failure is a DNS error that looks nothing like a configuration issue.
            config=BotoConfig(signature_version="s3v4", s3={"addressing_style": "path"}),
        )

    async def ensure_bucket(self) -> None:
        """Create the bucket when absent and set the staging lifecycle rule.

        Safe to call on every start and from several services at once (FD-1850): a
        `create_bucket` that loses the race to a peer answers `BucketAlreadyOwnedByYou`, which
        is success. `BucketAlreadyExists` means another owner in S3, so it is success only if
        `head_bucket` then succeeds; otherwise the original error is raised (chained to the head
        error), as is any other create failure.

        The rule (`RL-1724` DP-U1.2) expires `staging/` objects and aborts incomplete multipart
        uploads after `STAGING_EXPIRY_DAYS`; it is set here, not by an operator, so it holds
        under `docker compose up`.
        """

        def _ensure() -> None:
            try:
                self._client.head_bucket(Bucket=self._bucket)
            except ClientError:
                try:
                    self._client.create_bucket(Bucket=self._bucket)
                except ClientError as exc:
                    code = exc.response.get("Error", {}).get("Code")
                    if code == "BucketAlreadyOwnedByYou":
                        pass  # a peer created it between our head and create: ours
                    elif code == "BucketAlreadyExists":
                        # S3 means ANOTHER owner here. Only a head that now succeeds (our
                        # access, i.e. the race) is success; otherwise the original error.
                        try:
                            self._client.head_bucket(Bucket=self._bucket)
                        except ClientError as head_exc:
                            raise exc from head_exc
                    else:
                        raise
            # `put_bucket_lifecycle_configuration` replaces every rule on the bucket, so read
            # first and replace only this module's rule, by its ID: an operator's own rules
            # survive a restart.
            try:
                existing = self._client.get_bucket_lifecycle_configuration(Bucket=self._bucket)
                kept = [r for r in existing.get("Rules", []) if r.get("ID") != _STAGING_RULE_ID]
            except ClientError as exc:
                if exc.response.get("Error", {}).get("Code") != "NoSuchLifecycleConfiguration":
                    raise
                kept = []
            self._client.put_bucket_lifecycle_configuration(
                Bucket=self._bucket,
                LifecycleConfiguration={
                    "Rules": [
                        *kept,
                        {
                            "ID": _STAGING_RULE_ID,
                            "Status": "Enabled",
                            "Filter": {"Prefix": "staging/"},
                            "Expiration": {"Days": STAGING_EXPIRY_DAYS},
                            "AbortIncompleteMultipartUpload": {
                                "DaysAfterInitiation": STAGING_EXPIRY_DAYS
                            },
                        },
                    ]
                },
            )

        await asyncio.to_thread(_ensure)

    async def ping(self) -> None:
        """Cheapest call that proves the bucket is reachable and credentials work."""
        await asyncio.to_thread(self._client.head_bucket, Bucket=self._bucket)

    async def put(
        self,
        session: AsyncSession,
        content: bytes | Iterable[bytes],
        media_type: str,
    ) -> BlobRef:
        """Store content, take one reference for the caller, return its reference (FR-419, FR-420).

        Identical content stores no second object (FR-419) but still takes the caller's
        reference: a new row is written at `ref_count=1`, an existing one is retained. The
        caller is the owner, and writes the owning record in the same unit of work; a caller
        that does not leaks a reference, which can never lose data. No caller retains after
        a `put`.

        Requires the caller's transaction: the row is accounting, and accounting that
        commits independently of the change it belongs to is how a reference count drifts.
        """
        if not session.in_transaction():
            raise RuntimeError(
                "blobs.put() requires an open transaction — the blob row is accounting "
                "and must commit with the artifact that references it."
            )

        body = content if isinstance(content, bytes) else b"".join(content)
        digest = hashlib.sha256(body).hexdigest()

        # Shared, held to the caller's commit: the collector's object delete takes the same lock
        # exclusively, so it cannot delete the object between our read of the row and our insert.
        await _lock_digest(session, digest, shared=True)
        existing = await session.get(BlobRow, digest)
        if existing is not None:
            # FR-419 / ID-4: same content, same reference, no second object. Media type
            # is not part of the identity — the bytes are — so a mismatch is reported
            # rather than silently overwriting what another artifact already relies on.
            if existing.media_type != media_type:
                _log.info(
                    "blob already stored under a different media type",
                    extra={
                        "sha256": digest,
                        "stored_media_type": existing.media_type,
                        "requested_media_type": media_type,
                    },
                )
            try:
                await retain(session, digest)
            except PlatformError as exc:
                if exc.code != "BLOB_NOT_FOUND":
                    raise
                # The collector's DELETE committed between our read and this retain (it takes no
                # digest lock for the row delete, by design): the row is gone. The digest lock we
                # still hold keeps its object step waiting, so fall through to the new-object path
                # under it: upload, insert, and the collector then finds the row and keeps the
                # object (`re_put`). Drop the stale instance so a later `get` sees the new row.
                session.expunge(existing)
            else:
                return to_ref(existing)

        key = blob_key(digest)
        await asyncio.to_thread(
            self._client.put_object,
            Bucket=self._bucket,
            Key=key,
            Body=body,
            ContentType=media_type,
        )

        # Two first-time puts of the same bytes no longer exclude each other (the digest lock is
        # shared), so the second finds the row the first inserted only at the unique index:
        # on conflict it takes its reference with `retain` instead of failing.
        inserted = await session.execute(
            pg_insert(BlobRow)
            .values(sha256=digest, bytes_=len(body), media_type=media_type, ref_count=1)
            .on_conflict_do_nothing(index_elements=["sha256"])
            .returning(BlobRow.sha256)
        )
        if inserted.first() is None:
            await retain(session, digest)
        return BlobRef(sha256=digest, bytes=len(body), media_type=media_type)

    async def open(self, ref: BlobRef) -> AsyncIterator[bytes]:
        """Stream a blob's content back (`07` §5.2).

        Streamed rather than returned whole: a parquet dataset does not fit in the memory
        budget of an API process, and `07` R1 puts anything that might not finish quickly
        behind a Job rather than a buffered read.
        """
        key = blob_key(ref.sha256)
        try:
            response = await asyncio.to_thread(
                self._client.get_object, Bucket=self._bucket, Key=key
            )
        except ClientError as exc:
            raise PlatformError(
                "BLOB_NOT_FOUND",
                "Blob not found",
                404,
                f"No object stored at {key}.",
            ) from exc

        stream = response["Body"]
        try:
            while chunk := await asyncio.to_thread(stream.read, _CHUNK_SIZE):
                yield chunk
        finally:
            await asyncio.to_thread(stream.close)

    async def read(self, ref: BlobRef) -> bytes:
        """Read a blob whole. Only for content known to be small — see `open`."""
        return b"".join([chunk async for chunk in self.open(ref)])

    async def presign_download(self, ref: BlobRef, *, expires_in_s: int = 300) -> str:
        """A short-lived URL the client fetches directly (`07` §5.1, FR-421).

        Short-lived on purpose. The URL carries its own authorisation, so it is a bearer
        credential for those bytes — one pasted into a ticket should stop working before
        anyone reads the ticket. Five minutes is enough to start a download and not enough
        to be worth sharing.
        """
        url: str = await asyncio.to_thread(
            self._client.generate_presigned_url,
            "get_object",
            Params={"Bucket": self._bucket, "Key": blob_key(ref.sha256)},
            ExpiresIn=expires_in_s,
        )
        return url

    async def presign_upload(
        self, media_type: str, parts: int = 1, *, expires_in_s: int = 3600
    ) -> PresignedUpload:
        """Presigned URLs so large files never transit the API process (FR-421).

        The digest is not known until the client has uploaded, so the object lands under a
        staging key rather than at `blob/{sha}`: presigning the content address is impossible
        without the bytes, and asking the client for the digest first would let it choose
        one. The route records a Blob Upload for the result (`BlobUploadRow`), and
        `promote_upload` later moves the staged object to its content address and writes its
        `blobs` row (FR-1776).
        """
        if parts < 1:
            raise ValueError("parts must be at least 1")

        # Time-ordered so a lifecycle rule can expire abandoned staging objects by prefix,
        # and unguessable so one client cannot overwrite another's in-flight upload.
        staging_key = f"staging/{datetime.now(UTC):%Y/%m/%d}/{new_uuid7()}"

        if parts == 1:
            url = await asyncio.to_thread(
                self._client.generate_presigned_url,
                "put_object",
                Params={"Bucket": self._bucket, "Key": staging_key, "ContentType": media_type},
                ExpiresIn=expires_in_s,
            )
            return PresignedUpload(key=staging_key, urls=(url,), expires_in_s=expires_in_s)

        created = await asyncio.to_thread(
            self._client.create_multipart_upload,
            Bucket=self._bucket,
            Key=staging_key,
            ContentType=media_type,
        )
        upload_id = created["UploadId"]
        urls = [
            await asyncio.to_thread(
                self._client.generate_presigned_url,
                "upload_part",
                Params={
                    "Bucket": self._bucket,
                    "Key": staging_key,
                    "UploadId": upload_id,
                    "PartNumber": part,
                },
                ExpiresIn=expires_in_s,
            )
            for part in range(1, parts + 1)
        ]
        return PresignedUpload(
            upload_id=upload_id, key=staging_key, urls=tuple(urls), expires_in_s=expires_in_s
        )

    async def promote_upload(self, database: Database, upload_id: UUID) -> BlobRef:
        """Move a completed Blob Upload to its content address and own it (FR-1776).

        Runs in the `blob.promote` Job, never in a request (`07` R1). The staged bytes are read
        once, streamed, to compute the SHA-256; the object is copied server-side to
        `blob/{sha[:2]}/{sha}` unless a blob with that digest is stored (FR-419); then, in one
        transaction, the `blobs` row is written if absent, one reference is taken (FR-420) and
        the Blob Upload is marked promoted. Only after that commit is the staging object
        deleted. Idempotent per Blob Upload: a re-run of a promoted one returns the same ref and
        takes no second reference.
        """
        async with database.session() as session:
            upload = await session.get(BlobUploadRow, upload_id)
            if upload is None:
                raise PlatformError(
                    "NOT_FOUND", "Blob Upload not found", 404, f"No Blob Upload {upload_id}."
                )
            if upload.sha256 is not None:
                promoted = await session.get(BlobRow, upload.sha256)
                assert promoted is not None
                return to_ref(promoted)
            key, s3_upload_id = upload.staging_key, upload.s3_upload_id
            part_count, media_type = upload.part_count, upload.media_type

        await asyncio.to_thread(self._complete_staged, key, s3_upload_id, part_count)
        digest, size = await asyncio.to_thread(self._hash_object, key)
        content_key = blob_key(digest)

        async with database.session() as session:
            stored = await session.get(BlobRow, digest) is not None
        if not stored:
            await asyncio.to_thread(
                self._client.copy,
                {"Bucket": self._bucket, "Key": key},
                self._bucket,
                content_key,
                ExtraArgs={"ContentType": media_type, "MetadataDirective": "REPLACE"},
            )

        async with database.unit_of_work() as session:
            locked = await session.get(BlobUploadRow, upload_id, with_for_update=True)
            assert locked is not None
            if locked.sha256 is None:
                # The collector may have deleted this digest's row and object since the check
                # above. Under the digest lock nothing can change that until we commit: if no
                # row exists, make sure the object does, then insert the row.
                await _lock_digest(session, digest, shared=True)
                if await session.get(BlobRow, digest) is None and not await asyncio.to_thread(
                    self._object_exists, content_key
                ):
                    await asyncio.to_thread(
                        self._client.copy,
                        {"Bucket": self._bucket, "Key": key},
                        self._bucket,
                        content_key,
                        ExtraArgs={"ContentType": media_type, "MetadataDirective": "REPLACE"},
                    )
                insert = (
                    pg_insert(BlobRow)
                    .values(
                        sha256=digest,
                        bytes_=size,
                        media_type=media_type,
                        part_count=part_count if part_count > 1 else None,
                        ref_count=0,
                    )
                    .on_conflict_do_nothing(index_elements=["sha256"])
                )
                await session.execute(insert)
                try:
                    await retain(session, digest)
                except PlatformError as exc:
                    if exc.code != "BLOB_NOT_FOUND":
                        raise
                    # The row already existed (the insert did nothing) and the collector's DELETE,
                    # which takes no digest lock for the row delete, committed between the insert
                    # and this retain: the row is gone. Same as `put`: insert again (our own, new
                    # row; the collector cannot see it before we commit) and retain. The object is
                    # safe: the collector's object step waits on the shared lock we hold.
                    await session.execute(insert)
                    await retain(session, digest)
                locked.sha256 = digest
            # `populate_existing`: the instance read above may be the row the collector deleted.
            row = await session.get(BlobRow, digest, populate_existing=True)
            assert row is not None
            ref = to_ref(row)

        await asyncio.to_thread(self._client.delete_object, Bucket=self._bucket, Key=key)
        return ref

    def _object_exists(self, key: str) -> bool:
        try:
            self._client.head_object(Bucket=self._bucket, Key=key)
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") in {"404", "NoSuchKey", "NotFound"}:
                return False
            raise
        return True

    def _complete_staged(self, key: str, s3_upload_id: str | None, part_count: int) -> None:
        """Finish the staged object, or fail with `VALIDATION_FAILED` naming what is wrong.

        A multipart upload must have exactly parts 1 to `part_count`: S3 would complete from
        whatever parts it holds, promoting a truncated file as whole.
        """
        if s3_upload_id is None:
            try:
                self._client.head_object(Bucket=self._bucket, Key=key)
            except ClientError as exc:
                raise _validation(
                    "The upload is missing", f"No object was uploaded to {key}."
                ) from exc
            return

        parts: list[PartTypeDef] = []
        marker = 0
        try:
            while True:
                page = self._client.list_parts(
                    Bucket=self._bucket, Key=key, UploadId=s3_upload_id, PartNumberMarker=marker
                )
                parts.extend(page.get("Parts", []))
                if not page.get("IsTruncated"):
                    break
                marker = page["NextPartNumberMarker"]
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") != "NoSuchUpload":
                raise
            # A re-run after S3 completed the upload but before the row committed: the
            # multipart upload is gone and the object is whole.
            try:
                self._client.head_object(Bucket=self._bucket, Key=key)
            except ClientError as head_exc:
                raise _validation(
                    "The upload is missing", f"No object was uploaded to {key}."
                ) from head_exc
            return

        present = {int(part["PartNumber"]) for part in parts}
        missing = [n for n in range(1, part_count + 1) if n not in present]
        extra = sorted(present - set(range(1, part_count + 1)))
        if missing or extra:
            raise _validation(
                "The upload's parts are not the declared parts",
                f"Expected parts 1 to {part_count}; missing part(s) "
                f"{', '.join(map(str, missing)) or 'none'}"
                + (f"; unexpected part(s) {', '.join(map(str, extra))}" if extra else "")
                + ".",
            )
        try:
            self._client.complete_multipart_upload(
                Bucket=self._bucket,
                Key=key,
                UploadId=s3_upload_id,
                MultipartUpload={
                    "Parts": [
                        {"PartNumber": int(part["PartNumber"]), "ETag": part["ETag"]}
                        for part in sorted(parts, key=lambda p: int(p["PartNumber"]))
                    ]
                },
            )
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") == "EntityTooSmall":
                raise _validation(
                    "A part is below the store's minimum size",
                    "Every part but the last must be at least 5 MiB.",
                ) from exc
            raise

    def _hash_object(self, key: str) -> tuple[str, int]:
        """SHA-256 and size of the object at `key`, read once in `_CHUNK_SIZE` pieces."""
        stream = self._client.get_object(Bucket=self._bucket, Key=key)["Body"]
        digest, size = hashlib.sha256(), 0
        try:
            while chunk := stream.read(_CHUNK_SIZE):
                digest.update(chunk)
                size += len(chunk)
        finally:
            stream.close()
        return digest.hexdigest(), size

    # -- scratch (RL-857 §4, `docs/rulings/RL-00857-d6-chunk-checkpointed-resume
    # -built-in-the-job-handler-and-keyed-on-content-not-on-the-job.md`): a `score.batch` chunk
    # part, and the manifest that keys it, share one object — the key's own existence is the
    # manifest entry. Deliberately **not** content-addressed and never a `BlobRow`: a chunk part is
    # reproducible from (bundle content hash, Dataset Version reference, chunk index) rather than
    # identified by its bytes, so hashing it would buy nothing `blob_key` already buys for a real
    # artifact, and putting it under `blob/` would make FR-420's GC hold it for the 30-day grace
    # period after every crashed run. `staging/` above is the same idea for a different reason
    # (bytes with no digest yet); this is bytes that never get one. ------

    async def write_scratch(self, key: str, content: bytes) -> None:
        """Write (or overwrite) one scratch object at `scratch/{key}`.

        No transaction, no row: unlike `put`, there is no accounting to keep in step with
        anything else, which is exactly what makes a scratch part safe to write from
        outside a `unit_of_work`.
        """
        await asyncio.to_thread(
            self._client.put_object,
            Bucket=self._bucket,
            Key=f"scratch/{key}",
            Body=content,
            ContentType="application/octet-stream",
        )

    async def read_scratch(self, key: str) -> bytes | None:
        """The scratch object at `scratch/{key}`, or `None` if it does not exist.

        `None` rather than a raised `PlatformError` (contrast `open`/`read`, which serve a
        client's request and must refuse loudly): a caller checking a chunk's manifest
        entry needs to distinguish "not done yet" from every other failure, and a missing
        key is the expected, common case on every chunk this run has not reached before.
        """
        return await self.read_object(f"scratch/{key}")

    async def read_object(self, key: str) -> bytes | None:
        """The object at exactly `key`, or `None` if it does not exist."""
        try:
            response = await asyncio.to_thread(
                self._client.get_object, Bucket=self._bucket, Key=key
            )
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code")
            if code in ("NoSuchKey", "404"):
                return None
            raise
        body: bytes = await asyncio.to_thread(response["Body"].read)
        return body

    async def write_object(self, key: str, content: bytes) -> None:
        """Write the object at exactly `key`, with no accounting row (see `write_scratch`)."""
        await asyncio.to_thread(
            self._client.put_object,
            Bucket=self._bucket,
            Key=key,
            Body=content,
            ContentType="application/octet-stream",
        )

    async def delete_scratch(self, key: str) -> None:
        """Remove one scratch object. A missing key is not an error — deleting an already-
        deleted part is what a retried cleanup sweep does."""
        await asyncio.to_thread(
            self._client.delete_object, Bucket=self._bucket, Key=f"scratch/{key}"
        )

    async def list_scratch(self, prefix: str) -> list[str]:
        """Every scratch key under `scratch/{prefix}`, without the `scratch/` prefix
        itself — so a caller can round-trip a returned key straight back into
        `read_scratch`/`delete_scratch`. Paginated: a run with many chunks must not be
        capped at S3's 1,000-key page.
        """
        keys: list[str] = []
        continuation: str | None = None
        full_prefix = f"scratch/{prefix}"
        while True:
            kwargs: dict[str, Any] = {"Bucket": self._bucket, "Prefix": full_prefix}
            if continuation is not None:
                kwargs["ContinuationToken"] = continuation
            page = await asyncio.to_thread(self._client.list_objects_v2, **kwargs)
            keys.extend(
                obj["Key"].removeprefix("scratch/") for obj in page.get("Contents", [])
            )
            if not page.get("IsTruncated"):
                break
            continuation = page.get("NextContinuationToken")
        return keys

    async def collect_garbage(
        self,
        database: Database,
        *,
        actor: Principal,
        workspace_id: UUID,
        dry_run: bool = True,
        grace_days: int | None = None,
    ) -> GarbageCollectionReport:
        """Reclaim unreferenced blobs, conservatively (FR-420, #1855).

        A blob is deletable only when **all** hold: its count is 0, no owner row names it, and
        it is older than the grace period. The age check is what makes it conservative — a blob
        is created before the artifact that references it, so a GC run in that window would
        delete content that is about to be claimed.

        **The collector owns its transactions** (it takes the `Database`, not a session), because
        the order is the safety property:

        1. one unit of work deletes the rows by calling the owner-owned `SECURITY DEFINER`
           function `blob_gc_delete_unreferenced` (#1550 (c); `_delete_unreferenced` says what it
           does: lock the count-0 rows, delete those no owner row names with a snapshot taken
           after the locks, look again before the commit for an owner row that appeared) — and
           writes the audit event, then commits;
        2. only after that commit are the objects deleted, each under the digest's advisory lock
           and only if no row has appeared for it since (a concurrent `put` of the same bytes).

        A failure in step 2 leaves an object with no row (an orphan, cheap); it can never leave a
        row with no object, which is what a delete-then-rollback did. The audit event names the
        rows the statement actually deleted, not the ones a prior read expected to.

        **The caller holds no open transaction when it calls this** (#1855 (v)). The audit event
        takes the workspace's advisory lock, which a caller that holds an open transaction with an
        audit event for the same workspace already holds idle on the client side; PostgreSQL does
        not report that as a deadlock, so without a bound the call would never end. The first
        statement of the unit of work is therefore `SET LOCAL lock_timeout` (`GC_LOCK_TIMEOUT_S`
        seconds): on a timeout the run rolls back, nothing is deleted, and the call raises
        `BLOB_GC_LOCK_TIMEOUT`. The Job runner holds no transaction while a handler runs
        (`worker/tasks.py`, each status change is its own unit of work).

        `dry_run` defaults to **True**. A destructive sweep whose default is to destroy is
        a sweep someone runs by accident.
        """
        grace = grace_days if grace_days is not None else self._settings.blob_gc_grace_days
        cutoff = datetime.now(UTC) - timedelta(days=grace)

        try:
            report = await self._run_collection(
                database,
                actor=actor,
                workspace_id=workspace_id,
                dry_run=dry_run,
                grace=grace,
                cutoff=cutoff,
            )
        except DBAPIError as exc:
            coded = _coded_gc_error(exc)
            if coded is None:
                raise
            raise coded from exc

        re_put = [
            digest
            for digest in report.deleted
            if not await self._delete_object_if_unreferenced(database, digest)
        ]
        # `re_put` is known only after the audit event committed, so it is on the returned report
        # and in the log, not in the event: the event records the rows deleted.
        return report.model_copy(update={"re_put": tuple(re_put)}) if re_put else report

    async def _run_collection(
        self,
        database: Database,
        *,
        actor: Principal,
        workspace_id: UUID,
        dry_run: bool,
        grace: int,
        cutoff: datetime,
    ) -> GarbageCollectionReport:
        """The collector's first unit of work: delete the rows (or count them) and audit the run."""
        found: list[tuple[str, int]]
        async with database.unit_of_work() as session:
            # The FIRST statement: every lock this unit of work takes from here on, the row locks
            # of the delete and the workspace's audit lock, is bounded. A caller that breaks the
            # contract (it holds an open transaction that already holds that audit lock) gets a
            # coded error and a rolled-back run, not a hung job (#1855 (v)).
            await session.execute(text(f"SET LOCAL lock_timeout = {_GC_LOCK_TIMEOUT_MS}"))
            if dry_run:
                # The count-and-age selector only, deliberately without the owner re-check: a
                # dry run reports what the counts say, so a blob an owner names at count 0 (a
                # leaked undercount) shows in `considered` instead of being hidden by the guard
                # that would stop the real run from taking it.
                counted = await session.execute(
                    select(BlobRow.sha256, BlobRow.bytes_).where(
                        BlobRow.ref_count == 0, BlobRow.created_at < cutoff
                    )
                )
                found = [(row[0], int(row[1])) for row in counted.all()]
            else:
                found = await _delete_unreferenced(session, cutoff)
            report = GarbageCollectionReport(
                dry_run=dry_run,
                grace_days=grace,
                considered=len(found),
                deleted=() if dry_run else tuple(sha for sha, _ in found),
                bytes_reclaimed=0 if dry_run else sum(size for _, size in found),
            )
            # Audited either way (FR-420): a dry run is evidence about what the platform
            # believes is unreferenced, which is worth as much as the deletion itself.
            await audit.record(
                session,
                workspace_id=workspace_id,
                actor=actor,
                source=JobSource.SYSTEM,
                action="blob.garbage_collected",
                entity_ref="blob:gc@1",
                after=report.model_dump(mode="json"),
            )
        return report

    async def _delete_object_if_unreferenced(self, database: Database, digest: str) -> bool:
        """Delete one object whose row was just deleted; return False when the digest was re-put.

        Takes the digest lock **exclusively** (a `put` of the same bytes holds it shared from
        before its row read to its commit), then **re-reads that no `blobs` row exists** for the
        digest. A row that is there was re-created by a `put` after the row delete committed: the
        object is KEPT and the digest reported as re-put. The lock only orders the two sides; this
        re-read is what closes the race. Lock sites: see `_lock_digest`.
        """
        try:
            async with database.unit_of_work() as session:
                await _lock_digest(session, digest, shared=False)
                if await session.get(BlobRow, digest) is not None:
                    _log.info(
                        "blob re-put since its row was deleted; object kept",
                        extra={"sha256": digest},
                    )
                    return False
                await asyncio.to_thread(
                    self._client.delete_object, Bucket=self._bucket, Key=blob_key(digest)
                )
        except (ClientError, BotoCoreError):
            # The row is gone and committed; the object is an orphan, not a dangling reference. A
            # storage failure that is not a `ClientError` (an unreachable endpoint, a timeout) is a
            # `BotoCoreError`: it must not abort the loop and lose the report. The orphan sweep is
            # slice 3b's (`reconcile_orphans`); a database deadlock mid-loop is #1888's subject.
            _log.warning("blob object delete failed; left as an orphan", extra={"sha256": digest})
        return True


#: Namespace of the per-digest advisory lock, distinct from the audit chain's (`0x47495041`).
_DIGEST_LOCK_NAMESPACE: Final = 0x47495042


async def _lock_digest(session: AsyncSession, sha256: str, *, shared: bool) -> None:
    """Take the transaction-scoped advisory lock for one digest.

    It separates the writers of an object (`put`, `promote_upload`: write the object, then the
    row) from the collector's object delete. Without it a `put` that missed the row just after
    the collector's commit uploads the object, and the collector then deletes it, leaving a row
    with no bytes.

    **Writers take it SHARED, the collector EXCLUSIVE.** Writers need not exclude each other (the
    row's primary key does that), so two transactions locking `{A, B}` and `{B, A}` never block
    each other on this lock. (The `blobs` rows they then insert or update are locked until commit,
    so two `put`s in opposite orders can still deadlock on those rows, as before.) The collector
    waits for in-flight writers of that digest, and
    a writer waits for the collector's object step. Two digests that hash to one key only share
    or wait for each other. Released at commit or rollback.

    **Protocol:**

    - `BlobStore.put`: SHARED, taken **before** its row read, released at the caller's commit or
      rollback (an advisory `xact` lock has no other release).
    - `BlobStore.promote_upload`: SHARED, before its row read, released at the commit of its
      final unit of work.
    - `BlobStore._delete_object_if_unreferenced`: EXCLUSIVE, then the **re-read that no row
      exists**, then the object delete; released at that unit of work's commit, after the
      delete. A row found by the re-read keeps the object.
    """
    function = "pg_advisory_xact_lock_shared" if shared else "pg_advisory_xact_lock"
    await session.execute(
        text(f"SELECT {function}(:ns, hashtext(:sha))"),
        {"ns": _DIGEST_LOCK_NAMESPACE, "sha": sha256},
    )


async def retain(session: AsyncSession, sha256: str) -> int:
    """Take a reference to a blob. Returns the new count (FR-420)."""
    return await _adjust_ref_count(session, sha256, +1)


async def release(session: AsyncSession, sha256: str) -> int:
    """Release a reference. Returns the new count.

    A count that would go negative violates the check constraint and fails the transaction,
    rather than quietly reaching zero and making the blob eligible for deletion.

    **A release that reaches 0 while a row `BLOB_OWNERS` can see still names the blob is an
    internal invariant breach** (FR-420's second line of defence, #1504 D1): some writer made
    that owner without taking a reference, and finishing the release would let the collector
    delete a blob the owner reads. It raises `BLOB_REFERENCE_INVARIANT_BREACHED` (500), logs the
    digest and the owner count, and the caller's transaction rolls back with the decrement. The
    owner's own row must therefore stop naming the blob (and be flushed) before the release.
    Owners no query can see (`INSIDE_BLOB_OWNERS`) are outside the check.
    """
    count = await _adjust_ref_count(session, sha256, -1)
    if count == 0:
        # The session does not autoflush, so the owner query would not see a pending change.
        await session.flush()
        owners = await owner_count(session, sha256)
        if owners:
            _log.error(
                "blob release would reach zero while an owner still names it",
                extra={"sha256": sha256, "owner_count": owners},
            )
            raise PlatformError(
                "BLOB_REFERENCE_INVARIANT_BREACHED",
                "Internal error",
                500,
                "A blob reference count and its owners disagree.",
            )
    return count


async def owner_count(session: AsyncSession, sha256: str) -> int:
    """How many owner places `BLOB_OWNERS` finds naming this digest right now."""
    result = await session.execute(
        text(f"SELECT count(*) FROM ({_OWNER_ROWS_SQL}) AS owned WHERE sha256 = :sha"),
        {"sha": sha256},
    )
    return int(result.scalar_one())


async def _adjust_ref_count(session: AsyncSession, sha256: str, delta: int) -> int:
    result = await session.execute(
        update(BlobRow)
        .where(BlobRow.sha256 == sha256)
        .values(ref_count=BlobRow.ref_count + delta)
        .returning(BlobRow.ref_count)
    )
    row = result.first()
    if row is None:
        raise PlatformError(
            "BLOB_NOT_FOUND", "Blob not found", 404, f"No blob with digest {sha256}."
        )
    return int(row[0])


def _validation(title: str, detail: str) -> PlatformError:
    return PlatformError("VALIDATION_FAILED", title, 422, detail)


def to_ref(row: BlobRow) -> BlobRef:
    return BlobRef(
        sha256=row.sha256,
        bytes=row.bytes_,
        media_type=row.media_type,
        part_count=row.part_count,
    )


def blob_probe(store: BlobStore) -> Any:
    """Build the `/readyz` probe for the blob store (FR-444)."""

    async def probe() -> str | None:
        try:
            await store.ping()
        except Exception as exc:
            _log.warning("blob probe failed", extra={"error_type": type(exc).__name__})
            return f"unreachable: {type(exc).__name__}"
        return None

    return probe


#: Every column through which a **quote-input store** references a blob (NFR-499, RL-917).
#: A digest named here is never served by `GET /blobs/{sha256}` and never ingested, whoever
#: owns it otherwise: its body is read through that store's own workspace-scoped API. The
#: regression case store (`regression_runs.cases_blob_sha256`, FR-1221, WK-672 Slice 3) is the
#: second entry.
QUOTE_INPUT_BLOB_COLUMNS: tuple[Any, ...] = (
    ScoringTraceRow.blob_sha256,
    RegressionRunRow.cases_blob_sha256,
)


@dataclass(frozen=True)
class BlobOwner:
    """One place an artifact references a blob digest.

    `digests` is a `SELECT` returning one row per reference, in one column named `sha256`.
    """

    name: str
    digests: str


#: Every persisted place that references a blob by digest and is readable from PostgreSQL
#: (FR-420's precondition: every owner holds a reference). `put` takes the reference for a
#: new owner; this list is what a backfill recounts for owners that predate that, and what
#: the census test holds against the schema. An owner is added here when a table gains a
#: digest column or a JSONB path that carries one.
#:
#: Owners that name a blob from *inside another blob* are not here, because no query can see
#: them: the rate-table cell-diff chunks (named by the manifest blob) and a score batch's
#: output parquet (named by the Job's summary blob). See `INSIDE_BLOB_OWNERS`.
BLOB_OWNERS: tuple[BlobOwner, ...] = (
    BlobOwner(
        "dataset_versions.tables[*].blob",
        "SELECT t->'blob'->>'sha256' AS sha256 FROM dataset_versions, "
        "jsonb_array_elements(tables) AS t",
    ),
    BlobOwner(
        "jobs.result (kind = blob)",
        "SELECT result->>'ref' AS sha256 FROM jobs WHERE result->>'kind' = 'blob'",
    ),
    BlobOwner(
        "blob_uploads.sha256",
        "SELECT sha256 FROM blob_uploads",
    ),
    BlobOwner(
        "models.fit_result.booster_blob",
        "SELECT fit_result->'booster_blob'->>'sha256' AS sha256 FROM models",
    ),
    BlobOwner(
        "models.fit_result.covariance_blob",
        "SELECT fit_result->'covariance_blob'->>'sha256' AS sha256 FROM models",
    ),
    BlobOwner(
        "rate_table_versions.cells",
        "SELECT cells->>'sha256' AS sha256 FROM rate_table_versions",
    ),
    BlobOwner(
        "rating_versions.bundle.blob_sha256",
        "SELECT bundle->>'blob_sha256' AS sha256 FROM rating_versions",
    ),
    BlobOwner(
        "rating_versions.evidence.structural_diff_blob",
        "SELECT evidence->>'structural_diff_blob' AS sha256 FROM rating_versions",
    ),
    BlobOwner(
        "regression_runs.cases_blob_sha256",
        "SELECT cases_blob_sha256 AS sha256 FROM regression_runs",
    ),
    BlobOwner(
        "dislocation_runs.movers_blob_sha256",
        "SELECT movers_blob_sha256 AS sha256 FROM dislocation_runs",
    ),
    BlobOwner(
        "scoring_traces.blob_sha256",
        "SELECT blob_sha256 AS sha256 FROM scoring_traces",
    ),
)

#: Owners no query can see: they name the blob from inside another blob's body in S3.
#: `{name: reason}`. Blobs they hold are referenced by `put` when written (slice 1); the
#: legacy ones are the migration's conservative pin (see the revision that backfills).
INSIDE_BLOB_OWNERS: dict[str, str] = {
    "rate_table cell-diff chunks (manifest blob 'chunks')": (
        "named by the manifest blob that the Job's `result.ref` points at"
    ),
    "score batch output parquet (summary blob 'output_blob_sha256')": (
        "named by the summary blob that the Job's `result.ref` points at"
    ),
}

@dataclass(frozen=True)
class OwnerWriter:
    """One function that writes an owner place, and how it takes its reference (#1855 (iv)).

    `file::function` names it; `takes` is `put`, `retain` or `promote_upload` (its own body calls
    it, in the same transaction as the write), or another stated way: `via` names a helper in the
    same file whose body calls one, or `reason` says why no reference is taken here. The census
    test `test_blob_owner_writers.py` holds every entry against the code.
    """

    file: str
    function: str
    takes: str
    via: str = ""
    reason: str = ""


#: For each place in `BLOB_OWNERS`, the functions that write it. The rule the collector's safety
#: rests on: every writer takes a reference to the digest it names, in the same transaction as the
#: owner row, so the reference count protects the blob and a writer that follows the rule waits on
#: the row lock the collector holds (#1855 (iv)). Keyed by `BlobOwner.name`.
OWNER_WRITERS: dict[str, tuple[OwnerWriter, ...]] = {
    "dataset_versions.tables[*].blob": (
        OwnerWriter(
            "backend/src/app/data/ingestion.py", "ingest_upload", "via", via="_store_table"
        ),
        OwnerWriter("backend/src/app/data/ingestion.py", "correct_schema", "put"),
        OwnerWriter("backend/src/app/platform/datasets.py", "derive_version", "retain"),
        OwnerWriter(
            "backend/src/app/worker/data_handlers.py",
            "_derive.work",
            "via",
            via="_materialise_split",
        ),
        OwnerWriter("scripts/bench-score-batch.py", "_dataset_version", "put"),
    ),
    "jobs.result (kind = blob)": (
        OwnerWriter(
            "backend/src/app/platform/jobs.py",
            "transition",
            "earlier unit of work",
            reason=(
                "the result's digest was put, or promoted, with its reference in an earlier "
                "committed unit of work of the handler; this write names it and takes none of its "
                "own, and relies on that reference (the condition slice 3c carries forward: a Job "
                "result's blob keeps a reference while the Job row names it)"
            ),
        ),
    ),
    "blob_uploads.sha256": (
        OwnerWriter("backend/src/app/platform/blobs.py", "BlobStore.promote_upload", "retain"),
    ),
    "models.fit_result.booster_blob": (
        OwnerWriter(
            "backend/src/app/platform/modelling.py",
            "record_fit",
            "via",
            via="backend/src/app/worker/model_handlers.py::_fit.store",
        ),
    ),
    "models.fit_result.covariance_blob": (
        OwnerWriter(
            "backend/src/app/platform/modelling.py",
            "record_fit",
            "via",
            via="backend/src/app/worker/model_handlers.py::_fit.store",
        ),
    ),
    "rate_table_versions.cells": (
        OwnerWriter("backend/src/app/platform/rate_tables.py", "_persist_new_version", "put"),
    ),
    "rating_versions.bundle.blob_sha256": (
        OwnerWriter(
            "backend/src/app/platform/rating_versions.py",
            "record_bundle_blob",
            "via",
            via="backend/src/app/worker/rating_handlers.py::_rating_compile.work",
        ),
        OwnerWriter(
            "backend/src/app/platform/rating_versions.py",
            "compile_rating_version",
            "names nothing",
            reason="rewrites `bundle` without a `blob_sha256` key: it names no digest",
        ),
        OwnerWriter("scripts/bench-rating.py", "_seed", "put"),
    ),
    "rating_versions.evidence.structural_diff_blob": (
        OwnerWriter(
            "backend/src/app/platform/rating_versions.py",
            "submit_for_review",
            "via",
            via="_structural_diff_gate",
        ),
    ),
    "regression_runs.cases_blob_sha256": (
        OwnerWriter(
            "backend/src/app/platform/regression_runs.py",
            "persist_run",
            "via",
            via="backend/src/app/worker/rating_handlers.py::_rating_regression.persist",
        ),
    ),
    "dislocation_runs.movers_blob_sha256": (
        OwnerWriter(
            "backend/src/app/platform/dislocation_runs.py",
            "persist_run",
            "via",
            via="backend/src/app/worker/dislocation_handlers.py::_dislocation_run.persist",
        ),
    ),
    "scoring_traces.blob_sha256": (
        OwnerWriter("backend/src/app/platform/traces.py", "write_trace", "put"),
        OwnerWriter(
            "backend/src/app/platform/traces.py",
            "write_pending_trace",
            "names nothing",
            reason="writes `blob_sha256=None`: a pending row has no body yet",
        ),
        OwnerWriter("backend/src/app/platform/traces.py", "complete_pending_trace", "put"),
    ),
}

#: One row per reference, in a column named `sha256`, over every owner place.
_OWNER_ROWS_SQL = " UNION ALL ".join(f"({owner.digests})" for owner in BLOB_OWNERS)

_OWNER_COUNTS_SQL = (
    f"SELECT sha256, count(*) AS n FROM ({_OWNER_ROWS_SQL}) AS owned "
    "WHERE sha256 IS NOT NULL GROUP BY sha256"
)


#: The seconds every lock the collector's first unit of work takes may wait (#1855 (v)): its row
#: locks and the workspace's audit lock. A constant, stated in FR-420; a setting is added when a
#: deployment is shown to need another value.
GC_LOCK_TIMEOUT_S: Final = 10
_GC_LOCK_TIMEOUT_MS: Final = GC_LOCK_TIMEOUT_S * 1000


def render_gc_function_statements(
    owners: tuple[BlobOwner, ...] | None = None,
) -> tuple[str, str, str]:
    """The three statements of `blob_gc_delete_unreferenced`, as SQL text.

    `(lock, delete, recheck)`. This is the specification of the function body: the migration
    freezes the same text as a literal, a drift test holds the function's `prosrc` equal to it, and
    a later change to `BLOB_OWNERS` without a migration that replaces the function fails that test.
    `NOT EXISTS`, not `NOT IN`: a NULL digest from an owner place (an unpromoted upload, a model
    with no covariance blob) would make `NOT IN` match nothing, and collection would halt silently.
    """
    rows = " UNION ALL ".join(f"({owner.digests})" for owner in (owners or BLOB_OWNERS))
    lock = (
        "SELECT coalesce(array_agg(l.sha256), ARRAY[]::text[]) INTO v_locked FROM "
        "(SELECT blobs.sha256::text AS sha256 FROM blobs "
        "WHERE blobs.ref_count = 0 AND blobs.created_at < p_cutoff FOR UPDATE) AS l"
    )
    delete = (
        "WITH d AS (DELETE FROM blobs WHERE blobs.sha256 = ANY(v_locked) "
        "AND blobs.ref_count = 0 AND blobs.created_at < p_cutoff "
        f"AND NOT EXISTS (SELECT 1 FROM ({rows}) AS owned WHERE owned.sha256 = blobs.sha256) "
        "RETURNING blobs.sha256, blobs.bytes) "
        "SELECT coalesce(array_agg(d.sha256::text), ARRAY[]::text[]), "
        "coalesce(array_agg(d.bytes::bigint), ARRAY[]::bigint[]) INTO v_deleted, v_bytes FROM d"
    )
    recheck = (
        f"SELECT EXISTS (SELECT 1 FROM ({rows}) AS owned WHERE owned.sha256 = ANY(v_deleted)) "
        "INTO v_appeared"
    )
    return lock, delete, recheck


GC_FUNCTION_STATEMENTS: Final = render_gc_function_statements()

_GC_CALL = text("SELECT deleted_sha256, deleted_bytes FROM blob_gc_delete_unreferenced(:cutoff)")


async def _delete_unreferenced(session: AsyncSession, cutoff: datetime) -> list[tuple[str, int]]:
    """Delete every unreferenced blob row by calling the definer function; return
    `(sha256, bytes)` deleted.

    The decision lives in `blob_gc_delete_unreferenced` (#1550 (c)), owned by the owner role, so
    the application role needs no `DELETE` on `blobs` and no caller can skip a check. In one
    transaction it runs three statements (`render_gc_function_statements`):

    1. `SELECT … FOR UPDATE` the rows with count 0 created before `cutoff`. It waits for any
       transaction that holds one of those rows (a `retain` in flight) and, after the wait,
       re-evaluates the row's own `ref_count`: a row that was retained is not returned.
    2. A NEW `DELETE` of those rows that no owner row names, with a snapshot taken **after** the
       row locks are held: an owner row that committed while statement 1 waited is seen.
    3. With a fresh snapshot, still holding the locks, a look for an owner row that names a digest
       statement 2 deleted. If one exists the function raises and the run rolls back, so nothing
       is deleted (`BLOB_GC_OWNER_APPEARED`).

    What this covers and what it does not (#1893 review, #1855 (iv)). The safety rests on the
    reference count: every owner writer takes a reference with `put`, `retain` or `promote_upload`
    in its own transaction (a census test holds that), and such a writer's `retain` waits on the
    row lock of statement 1. Statement 3 is a second line for a writer that breaks the rule: an
    owner row that commits without a reference while statement 2 runs is seen by statement 3 and
    refused. **Not covered:** an owner row that commits without a reference after statement 3's
    snapshot and before the commit; no row lock on `blobs` stops that, because such a writer
    touches only the owner table. Probed on a copy database with a delay planted inside the
    `DELETE`, against the one-statement form: the row and its object were deleted while an owner
    row named the digest. A function that deletes nothing and reports nothing (a cutoff younger
    than one day) is refused as `BLOB_GC_CUTOFF_TOO_RECENT`.
    """
    result = await session.execute(_GC_CALL, {"cutoff": cutoff})
    return [(row[0], int(row[1])) for row in result.all()]


def _coded_gc_error(exc: DBAPIError) -> PlatformError | None:
    """Map a database error from the collector's first unit of work to its registered code.

    `55P03` (`lock_not_available`) is the lock timeout: `BLOB_GC_LOCK_TIMEOUT`, 503. The function's
    own refusals carry their code as the first word of the message. Anything else is not the
    collector's to name and is returned as `None`.
    """
    orig = exc.orig
    sqlstate = getattr(orig, "sqlstate", None)
    message = str(orig)
    if sqlstate == "55P03":
        return PlatformError(
            "BLOB_GC_LOCK_TIMEOUT",
            "Blob collection timed out waiting for a lock",
            503,
            f"A lock was not available within {GC_LOCK_TIMEOUT_S} s; nothing was deleted. "
            "The caller must hold no open transaction when it calls the collector.",
        )
    if "BLOB_GC_OWNER_APPEARED" in message:
        return PlatformError(
            "BLOB_GC_OWNER_APPEARED",
            "An owner row appeared for a blob the collector was deleting",
            409,
            "An owner row naming a deleted digest was committed during the run; the run was "
            "rolled back and nothing was deleted.",
        )
    if "BLOB_GC_CUTOFF_TOO_RECENT" in message:
        return PlatformError(
            "BLOB_GC_CUTOFF_TOO_RECENT",
            "The collection cutoff is too recent",
            422,
            "The cutoff is inside the one-day floor the database enforces.",
        )
    return None


async def backfill_ref_counts(session: AsyncSession) -> int:
    """Raise every blob's `ref_count` to the number of owners that reference it; return how
    many rows moved. Never lowers a count: a reference that is held and not counted is a
    leak, and a leak can never lose data (FR-420)."""
    result = await session.execute(
        text(
            "UPDATE blobs SET ref_count = owned.n FROM (" + _OWNER_COUNTS_SQL + ") AS owned "
            "WHERE blobs.sha256 = owned.sha256 AND blobs.ref_count < owned.n"
        )
    )
    return int(cast("CursorResult[Any]", result).rowcount)


def blob_not_found(sha256: str) -> PlatformError:
    """The one answer for "no such blob", "a quote input" and "not yours", so no route
    confirms that a digest exists (`07` §5.1, 2026-09-28)."""
    return PlatformError("NOT_FOUND", "Blob not found", 404, f"No blob with digest {sha256}.")


async def blob_readable_by(session: AsyncSession, *, sha256: str, workspace_id: UUID) -> bool:
    """Whether a caller in `workspace_id` may read blob `sha256`: download it, or ingest it.

    `blobs` has no workspace column — a blob is content-addressed, and one digest can be
    owned in two workspaces — so the answer comes from the rows that reference it. Refused
    first if any quote-input store references it; then readable only if an **owner in the
    caller's workspace** references it: a dataset version's table (this route's declared
    purpose) or a job's `JobResult(kind="blob")` (`03` §5.2). Anything else, including a
    blob nothing references, is refused: the list of owners is an allow-list.
    """
    for column in QUOTE_INPUT_BLOB_COLUMNS:
        if (await session.execute(select(column).where(column == sha256).limit(1))).first():
            return False
    owners = (
        select(DatasetVersionRow.id).where(
            DatasetVersionRow.workspace_id == workspace_id,
            DatasetVersionRow.tables.contains([{"blob": {"sha256": sha256}}]),
        ),
        select(JobRow.id).where(
            JobRow.workspace_id == workspace_id,
            JobRow.result.contains({"kind": "blob", "ref": sha256}),
        ),
    )
    for owner in owners:
        if (await session.execute(owner.limit(1))).first():
            return True
    return False
