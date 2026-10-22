"""FR-418, FR-419, FR-420, FR-421 and ID-4 — content addressing, dedup, refcounts, conservative GC.

Against real MinIO and real PostgreSQL. Deduplication is a primary-key behaviour and
presigning is an S3 signature behaviour; neither is testable against a double.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta

import pytest
from botocore.exceptions import ClientError
from sqlalchemy import select, update

from app.db.models import AuditEventRow, BlobRow
from app.db.session import Database
from app.errors import PlatformError
from app.platform import blobs
from app.platform.blobs import BlobStore, blob_key
from model_schema import BlobRef, new_uuid7

TEXT = b"policy_id,exposure,claims\nP1,1.0,0\n"
TEXT_SHA = hashlib.sha256(TEXT).hexdigest()


def unique(label: bytes) -> bytes:
    """Content that no earlier run has already stored.

    Content addressing plus a persistent database means identical bytes carry their
    reference count across test runs — a test asserting `ref_count == 1` passes once and
    then fails for ever. Deduplication working correctly is exactly what makes fixed test
    payloads stateful.
    """
    return label + b" " + str(new_uuid7()).encode()


@pytest.mark.req("FR-418")
def test_key_layout_shards_by_digest_prefix() -> None:
    """`blob/{sha256[:2]}/{sha256}` — a flat namespace degrades at millions of objects."""
    assert blob_key(TEXT_SHA) == f"blob/{TEXT_SHA[:2]}/{TEXT_SHA}"


@pytest.mark.req("FR-418")
async def test_put_stores_content_and_records_size_and_type(
    database: Database, blob_store: BlobStore
) -> None:
    async with database.unit_of_work() as session:
        ref = await blob_store.put(session, TEXT, "text/csv")

    assert ref.sha256 == TEXT_SHA
    assert ref.bytes_ == len(TEXT)
    assert ref.media_type == "text/csv"

    async with database.session() as session:
        row = await session.get(BlobRow, TEXT_SHA)
    assert row is not None
    assert row.bytes_ == len(TEXT)
    assert row.ref_count == 0


@pytest.mark.req("FR-419")
async def test_identical_content_is_stored_once(
    database: Database, blob_store: BlobStore
) -> None:
    """FR-419: writing identical content is a no-op returning the existing reference."""
    payload = unique(b"identical bytes")
    async with database.unit_of_work() as session:
        first = await blob_store.put(session, payload, "application/octet-stream")
    async with database.unit_of_work() as session:
        second = await blob_store.put(session, payload, "application/octet-stream")

    assert first == second

    async with database.session() as session:
        rows = (
            await session.execute(select(BlobRow).where(BlobRow.sha256 == first.sha256))
        ).scalars().all()
    assert len(rows) == 1


@pytest.mark.req("FR-419")
async def test_different_content_gets_a_different_reference(
    database: Database, blob_store: BlobStore
) -> None:
    async with database.unit_of_work() as session:
        a = await blob_store.put(session, b"alpha", "text/plain")
        b = await blob_store.put(session, b"beta", "text/plain")
    assert a.sha256 != b.sha256


@pytest.mark.req("FR-418")
async def test_content_round_trips_byte_for_byte(
    database: Database, blob_store: BlobStore
) -> None:
    payload = bytes(range(256)) * 40
    async with database.unit_of_work() as session:
        ref = await blob_store.put(session, payload, "application/octet-stream")
    assert await blob_store.read(ref) == payload


@pytest.mark.req("FR-418")
async def test_streaming_read_reassembles_the_content(
    database: Database, blob_store: BlobStore
) -> None:
    """A parquet dataset does not fit in an API process's memory budget."""
    payload = b"x" * (3 * 1024 * 1024)
    async with database.unit_of_work() as session:
        ref = await blob_store.put(session, payload, "application/octet-stream")

    chunks = [chunk async for chunk in blob_store.open(ref)]
    assert len(chunks) > 1
    assert b"".join(chunks) == payload


@pytest.mark.req("FR-418")
async def test_put_requires_a_transaction(database: Database, blob_store: BlobStore) -> None:
    """Negative: the row is accounting; accounting that commits alone drifts."""
    async with database.session() as session:
        with pytest.raises(RuntimeError, match="requires an open transaction"):
            await blob_store.put(session, b"anything", "text/plain")


@pytest.mark.req("FR-418")
async def test_reading_a_missing_blob_is_a_typed_error(blob_store: BlobStore) -> None:
    missing = BlobRef(sha256="0" * 64, bytes=1, media_type="text/plain")
    with pytest.raises(PlatformError) as exc:
        await blob_store.read(missing)
    assert exc.value.code == "BLOB_NOT_FOUND"
    assert exc.value.status_code == 404


@pytest.mark.req("FR-420")
async def test_reference_counting_tracks_retain_and_release(
    database: Database, blob_store: BlobStore
) -> None:
    async with database.unit_of_work() as session:
        ref = await blob_store.put(session, unique(b"counted"), "text/plain")
        assert await blobs.retain(session, ref.sha256) == 1
        assert await blobs.retain(session, ref.sha256) == 2
        assert await blobs.release(session, ref.sha256) == 1


@pytest.mark.req("FR-420")
async def test_releasing_below_zero_fails_the_transaction(
    database: Database, blob_store: BlobStore
) -> None:
    """Negative: a silent negative count makes a referenced blob look collectable."""
    from sqlalchemy.exc import IntegrityError

    async with database.unit_of_work() as session:
        ref = await blob_store.put(session, unique(b"never retained"), "text/plain")

    with pytest.raises(IntegrityError):
        async with database.unit_of_work() as session:
            await blobs.release(session, ref.sha256)


@pytest.mark.req("FR-420")
async def test_retaining_a_missing_blob_is_a_typed_error(database: Database) -> None:
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await blobs.retain(session, "f" * 64)
    assert exc.value.code == "BLOB_NOT_FOUND"


@pytest.mark.req("FR-420")
async def test_gc_defaults_to_dry_run_and_deletes_nothing(
    database: Database, blob_store: BlobStore, workspace_id, principal
) -> None:
    """A destructive sweep whose default is to destroy is one that gets run by accident."""
    async with database.unit_of_work() as session:
        ref = await blob_store.put(session, unique(b"gc dry run"), "text/plain")
    await _age_blob(database, ref.sha256, days=60)

    async with database.unit_of_work() as session:
        report = await blob_store.collect_garbage(
            session, actor=principal, workspace_id=workspace_id
        )

    assert report.dry_run is True
    assert report.deleted == ()
    assert report.considered >= 1

    async with database.session() as session:
        assert await session.get(BlobRow, ref.sha256) is not None


@pytest.mark.req("FR-420")
async def test_gc_spares_a_referenced_blob(
    database: Database, blob_store: BlobStore, workspace_id, principal
) -> None:
    """Negative: collecting a referenced blob deletes a dataset someone still points at."""
    async with database.unit_of_work() as session:
        ref = await blob_store.put(session, unique(b"still referenced"), "text/plain")
        await blobs.retain(session, ref.sha256)
    await _age_blob(database, ref.sha256, days=60)

    async with database.unit_of_work() as session:
        report = await blob_store.collect_garbage(
            session, actor=principal, workspace_id=workspace_id, dry_run=False
        )

    assert ref.sha256 not in report.deleted
    async with database.session() as session:
        assert await session.get(BlobRow, ref.sha256) is not None


@pytest.mark.req("FR-420")
async def test_gc_spares_a_young_unreferenced_blob(
    database: Database, blob_store: BlobStore, workspace_id, principal
) -> None:
    """A blob exists before the artifact that references it — the grace period is that gap."""
    async with database.unit_of_work() as session:
        ref = await blob_store.put(session, unique(b"just uploaded"), "text/plain")

    async with database.unit_of_work() as session:
        report = await blob_store.collect_garbage(
            session, actor=principal, workspace_id=workspace_id, dry_run=False
        )

    assert ref.sha256 not in report.deleted
    async with database.session() as session:
        assert await session.get(BlobRow, ref.sha256) is not None


@pytest.mark.req("FR-420")
async def test_gc_deletes_an_old_unreferenced_blob_and_audits_it(
    database: Database, blob_store: BlobStore, workspace_id, principal
) -> None:
    async with database.unit_of_work() as session:
        ref = await blob_store.put(session, unique(b"collect me"), "text/plain")
    await _age_blob(database, ref.sha256, days=60)

    async with database.unit_of_work() as session:
        report = await blob_store.collect_garbage(
            session, actor=principal, workspace_id=workspace_id, dry_run=False
        )

    assert ref.sha256 in report.deleted
    assert report.bytes_reclaimed > 0

    async with database.session() as session:
        assert await session.get(BlobRow, ref.sha256) is None
        actions = [
            e.action
            for e in (
                await session.execute(
                    select(AuditEventRow).where(AuditEventRow.workspace_id == workspace_id)
                )
            ).scalars()
        ]
    assert actions == ["blob.garbage_collected"]

    with pytest.raises(PlatformError):
        await blob_store.read(ref)


@pytest.mark.req("FR-421")
async def test_presigned_single_part_upload_is_usable(blob_store: BlobStore) -> None:
    """The URL must actually accept the bytes — a signature that only looks right is not one."""
    import httpx

    upload = await blob_store.presign_upload("text/csv")
    assert upload.upload_id is None
    assert len(upload.urls) == 1

    async with httpx.AsyncClient() as client:
        response = await client.put(
            upload.urls[0], content=TEXT, headers={"Content-Type": "text/csv"}
        )
    assert response.status_code == 200


@pytest.mark.req("FR-421")
async def test_presigned_multipart_returns_one_url_per_part(blob_store: BlobStore) -> None:
    upload = await blob_store.presign_upload("application/octet-stream", parts=3)
    assert upload.upload_id is not None
    assert len(upload.urls) == 3
    assert len(set(upload.urls)) == 3


@pytest.mark.req("FR-421")
async def test_presign_rejects_zero_parts(blob_store: BlobStore) -> None:
    with pytest.raises(ValueError, match="at least 1"):
        await blob_store.presign_upload("text/plain", parts=0)


@pytest.mark.req("NFR-532")
async def test_no_credential_survives_a_settings_dump() -> None:
    """R3 / NFR-532: a settings object reaching a log line must not carry secrets.

    Every credential is given a distinctive value, so the assertion is about the property
    — no secret escapes — rather than about a substring that legitimately appears
    elsewhere. The first version of this test asserted the store's *username* was absent
    and passed locally only because CI, not the developer machine, sets `GIP_DATABASE_URL`.
    """
    from pydantic import SecretStr

    from app.config import Settings

    settings = Settings(
        database_url=SecretStr("postgresql+asyncpg://u:db-pw-alpha@localhost:5432/d"),
        redis_url=SecretStr("redis://:redis-pw-bravo@localhost:6379/0"),
        blob_access_key=SecretStr("blob-key-charlie"),
        blob_secret_key=SecretStr("blob-pw-delta"),
    )
    secrets = ("db-pw-alpha", "redis-pw-bravo", "blob-key-charlie", "blob-pw-delta")

    for rendered in (repr(settings), str(settings.model_dump()), settings.model_dump_json()):
        for secret in secrets:
            assert secret not in rendered


async def _age_blob(database: Database, sha256: str, *, days: int) -> None:
    """Backdate a blob so the grace period can be exercised without waiting 30 days."""
    async with database.unit_of_work() as session:
        await session.execute(
            update(BlobRow)
            .where(BlobRow.sha256 == sha256)
            .values(created_at=datetime.now(UTC) - timedelta(days=days))
        )


@pytest.mark.req("FR-421")
async def test_ensure_bucket_sets_the_staging_lifecycle_rule(blob_store: BlobStore) -> None:
    """RL-1724 DP-U1.2: staged objects and incomplete multipart uploads expire after 2 days."""
    await blob_store.ensure_bucket()
    config = blob_store._client.get_bucket_lifecycle_configuration(Bucket=blob_store._bucket)
    prefixes = {
        rule.get("Filter", {}).get("Prefix") or rule.get("Prefix") for rule in config["Rules"]
    }
    assert "staging/" in prefixes


@pytest.mark.req("FR-421")
async def test_ensure_bucket_keeps_a_rule_it_does_not_own(blob_store: BlobStore) -> None:
    """Breaker: PUT the lifecycle configuration without reading it -> the operator's rule is
    gone after a restart, and so is every other rule on the bucket."""
    client, bucket = blob_store._client, blob_store._bucket
    foreign = {
        "ID": "operator-expire-tmp",
        "Status": "Enabled",
        "Filter": {"Prefix": "tmp/"},
        "Expiration": {"Days": 9},
    }
    client.put_bucket_lifecycle_configuration(
        Bucket=bucket, LifecycleConfiguration={"Rules": [foreign]}
    )
    try:
        await blob_store.ensure_bucket()
        await blob_store.ensure_bucket()  # idempotent: our rule is replaced, not duplicated
        ids = [r["ID"] for r in client.get_bucket_lifecycle_configuration(Bucket=bucket)["Rules"]]
        assert sorted(ids) == ["expire-staging", "operator-expire-tmp"]
    finally:
        client.delete_bucket_lifecycle(Bucket=bucket)
        await blob_store.ensure_bucket()


@pytest.mark.req("FR-421")
async def test_ensure_bucket_sets_the_rule_on_a_bucket_with_no_configuration(
    blob_store: BlobStore,
) -> None:
    """A bucket with no lifecycle configuration answers `NoSuchLifecycleConfiguration`; that is
    the first-start case, not an error."""
    client, bucket = blob_store._client, blob_store._bucket
    client.delete_bucket_lifecycle(Bucket=bucket)
    await blob_store.ensure_bucket()
    rules = client.get_bucket_lifecycle_configuration(Bucket=bucket)["Rules"]
    assert [r["ID"] for r in rules] == ["expire-staging"]


def _client_error(code: str, operation: str) -> ClientError:
    return ClientError({"Error": {"Code": code, "Message": code}}, operation)


class _StagedStub:
    """Stands in for the S3 client where the real store cannot be made to answer as needed."""

    def __init__(self, *, list_parts: Exception, head: Exception | None) -> None:
        self._list_parts, self._head = list_parts, head
        self.head_calls = 0

    def list_parts(self, **_: object) -> dict[str, object]:
        raise self._list_parts

    def head_object(self, **_: object) -> dict[str, object]:
        self.head_calls += 1
        if self._head is not None:
            raise self._head
        return {}


@pytest.mark.req("FR-421")
async def test_completing_a_finished_multipart_upload_again_finds_the_object(
    blob_store: BlobStore,
) -> None:
    """S3 completed the upload but the row did not commit: the multipart upload is gone
    (`NoSuchUpload`) and the object is whole, so the retry succeeds.

    Breaker: re-raise `NoSuchUpload` -> the retry fails for ever on a promoted object."""
    stub = _StagedStub(list_parts=_client_error("NoSuchUpload", "ListParts"), head=None)
    blob_store._client = stub
    blob_store._complete_staged("staging/k", "gone", 2)
    assert stub.head_calls == 1


@pytest.mark.req("FR-421")
async def test_a_gone_multipart_upload_with_no_object_is_the_named_failure(
    blob_store: BlobStore,
) -> None:
    """Breaker: leave the `head_object` after `NoSuchUpload` unguarded -> a raw `ClientError`
    reaches the Job as an unclassified failure."""
    stub = _StagedStub(
        list_parts=_client_error("NoSuchUpload", "ListParts"),
        head=_client_error("404", "HeadObject"),
    )
    blob_store._client = stub
    with pytest.raises(PlatformError) as caught:
        blob_store._complete_staged("staging/k", "gone", 2)
    assert caught.value.code == "VALIDATION_FAILED"
    assert caught.value.title == "The upload is missing"


class _RacingS3:
    """S3 client stub for a concurrent first start (FD 8169): the bucket is absent at
    `head_bucket`, a peer creates it before our `create_bucket`, so that call raises
    `create_code`. After that the bucket exists unless `head_after` says otherwise."""

    def __init__(self, create_code: str, *, head_after: str | None = None) -> None:
        self.create_code = create_code
        self.head_after = head_after
        self.heads = 0
        self.lifecycle: dict[str, object] | None = None

    def head_bucket(self, Bucket: str) -> None:  # noqa: N803 - boto3 keyword names
        self.heads += 1
        if self.heads == 1:
            raise _client_error("404", "HeadBucket")
        if self.head_after is not None:
            raise _client_error(self.head_after, "HeadBucket")

    def create_bucket(self, Bucket: str) -> None:  # noqa: N803
        raise _client_error(self.create_code, "CreateBucket")

    def get_bucket_lifecycle_configuration(self, Bucket: str) -> dict[str, object]:  # noqa: N803
        raise _client_error("NoSuchLifecycleConfiguration", "GetBucketLifecycleConfiguration")

    def put_bucket_lifecycle_configuration(
        self,
        Bucket: str,  # noqa: N803
        LifecycleConfiguration: dict[str, object],  # noqa: N803
    ) -> None:
        self.lifecycle = LifecycleConfiguration


def _store_with(client: _RacingS3) -> BlobStore:
    store = BlobStore.__new__(BlobStore)
    store._bucket = "race-bucket"
    store._client = client  # type: ignore[assignment]
    return store


@pytest.mark.req("FR-421")
@pytest.mark.parametrize("code", ["BucketAlreadyOwnedByYou", "BucketAlreadyExists"])
async def test_ensure_bucket_survives_losing_the_create_race(code: str) -> None:
    """FD 8169: two services starting together both see no bucket; the loser's
    `create_bucket` answers `code`. That is success, and the lifecycle rule is still set."""
    client = _RacingS3(code)
    await _store_with(client).ensure_bucket()
    assert client.lifecycle is not None
    assert client.heads == 2  # the bucket was re-checked, not assumed


@pytest.mark.req("FR-421")
async def test_ensure_bucket_still_fails_when_the_existing_bucket_is_not_ours() -> None:
    """Breaker: `BucketAlreadyExists` for a bucket we cannot reach (another account's) is
    not success -- swallowing it would leave every later call failing far from the cause."""
    client = _RacingS3("BucketAlreadyExists", head_after="403")
    with pytest.raises(ClientError):
        await _store_with(client).ensure_bucket()
    assert client.lifecycle is None


@pytest.mark.req("FR-421")
async def test_ensure_bucket_reraises_any_other_create_failure() -> None:
    client = _RacingS3("AccessDenied")
    with pytest.raises(ClientError):
        await _store_with(client).ensure_bucket()
    assert client.lifecycle is None
