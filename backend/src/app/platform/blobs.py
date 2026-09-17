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
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any, Final

import boto3
from botocore.client import Config as BotoConfig
from botocore.exceptions import ClientError
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.db.models import BlobRow
from app.errors import PlatformError
from app.observability.logging import get_logger
from app.platform import audit
from model_schema import BlobRef, JobSource, Principal, new_uuid7

if TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_s3.client import S3Client

__all__ = [
    "BlobStore",
    "GarbageCollectionReport",
    "PresignedUpload",
    "blob_key",
    "blob_probe",
    "to_ref",
]

_log = get_logger("app.blobs")

_CHUNK_SIZE: Final = 1024 * 1024  # 1 MiB


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
        """Create the bucket when absent. Idempotent, so startup can always call it."""

        def _ensure() -> None:
            try:
                self._client.head_bucket(Bucket=self._bucket)
            except ClientError:
                self._client.create_bucket(Bucket=self._bucket)

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
        """Store content and return its reference. Identical content is a no-op (FR-419).

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
            return to_ref(existing)

        key = blob_key(digest)
        await asyncio.to_thread(
            self._client.put_object,
            Bucket=self._bucket,
            Key=key,
            Body=body,
            ContentType=media_type,
        )

        session.add(
            BlobRow(sha256=digest, bytes_=len(body), media_type=media_type, ref_count=0)
        )
        await session.flush()
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
        staging key and is promoted to its content address on completion. Presigning
        `blob/{sha}` directly is impossible without the bytes, and asking the client for
        the digest first would let it choose one.
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

    # -- scratch (RL-857 §4, `docs/rulings/RL-00857-d6-chunk-checkpointed-resume
    # -built-in-the-job-handler-and-keyed-on-content-not-on-the-job.md`): a `score.batch` chunk part, and the manifest that keys it, share one
    # object — the key's own existence is the manifest entry. Deliberately **not**
    # content-addressed and never a `BlobRow`: a chunk part is reproducible from
    # (bundle content hash, Dataset Version reference, chunk index) rather than identified
    # by its bytes, so hashing it would buy nothing `blob_key` already buys for a real
    # artifact, and putting it under `blob/` would make FR-420's GC hold it for the
    # 30-day grace period after every crashed run. `staging/` above is the same idea for a
    # different reason (bytes with no digest yet); this is bytes that never get one. ------

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
        try:
            response = await asyncio.to_thread(
                self._client.get_object, Bucket=self._bucket, Key=f"scratch/{key}"
            )
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code")
            if code in ("NoSuchKey", "404"):
                return None
            raise
        body: bytes = await asyncio.to_thread(response["Body"].read)
        return body

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
        session: AsyncSession,
        *,
        actor: Principal,
        workspace_id: Any,
        dry_run: bool = True,
        grace_days: int | None = None,
    ) -> GarbageCollectionReport:
        """Reclaim unreferenced blobs, conservatively (FR-420).

        A blob is deletable only when **both** hold: nothing references it, and it is older
        than the grace period. The age check is what makes it conservative — a blob is
        created before the artifact that references it, so a GC run in that window would
        delete content that is about to be claimed.

        `dry_run` defaults to **True**. A destructive sweep whose default is to destroy is
        a sweep someone runs by accident.
        """
        grace = grace_days if grace_days is not None else self._settings.blob_gc_grace_days
        cutoff = datetime.now(UTC) - timedelta(days=grace)

        candidates = (
            await session.execute(
                select(BlobRow).where(BlobRow.ref_count == 0, BlobRow.created_at < cutoff)
            )
        ).scalars().all()

        report = GarbageCollectionReport(
            dry_run=dry_run,
            grace_days=grace,
            considered=len(candidates),
            deleted=tuple(b.sha256 for b in candidates) if not dry_run else (),
            bytes_reclaimed=sum(b.bytes_ for b in candidates) if not dry_run else 0,
        )

        if not dry_run:
            for blob in candidates:
                await asyncio.to_thread(
                    self._client.delete_object,
                    Bucket=self._bucket,
                    Key=blob_key(blob.sha256),
                )
                await session.delete(blob)
            await session.flush()

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


async def retain(session: AsyncSession, sha256: str) -> int:
    """Take a reference to a blob. Returns the new count (FR-420)."""
    return await _adjust_ref_count(session, sha256, +1)


async def release(session: AsyncSession, sha256: str) -> int:
    """Release a reference. Returns the new count.

    A count that would go negative violates the check constraint and fails the transaction,
    rather than quietly reaching zero and making the blob eligible for deletion.
    """
    return await _adjust_ref_count(session, sha256, -1)


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
