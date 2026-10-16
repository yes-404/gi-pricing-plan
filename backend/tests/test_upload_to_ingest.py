"""A file goes from disk to a `succeeded` Dataset Version through the public API alone.

`07` FR-421 (presigned uploads), the completion step that FD-1730 found unbuilt, and `01`
FR-27 (ingestion). This is the test that would have caught the gap: every other ingest test
seeds an owned blob, so none of them could notice that no public path produces one.

**No seeding** (RL-1724, the 11:24:38 BST carve-out): this file writes no row the path under
test would otherwise create. It imports no blob fixture and opens no database session.
`principal` and `grant` are identity, not seeding.

**A real worker** (RL-1724 DP-U2, W2): a separate Celery process launched from the unmodified
entrypoint, consuming `io` only. This file never imports the entrypoint and never runs a
job itself. The Job reaches the worker through the outbox relay and Redis.
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import subprocess
import sys
import time
from collections.abc import Iterator
from pathlib import Path

import httpx
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from app.api.deps import DEV_PRINCIPAL_HEADER
from app.config import Settings
from app.db.session import Database
from app.platform import outbox
from app.worker.celery_app import build_celery
from app.worker.tasks import CeleryPublisher

PART_ONE_BYTES = 5 * 1024 * 1024  # S3's minimum for every part but the last


def _csv() -> bytes:
    """Part one is exactly 5 MiB of whole rows, so the split falls on a row boundary."""
    header = b"Policy ID,Exposure Years,Claim Count,Claim Amount Minor,Vehicle Group\n"
    rows: list[bytes] = []
    size = len(header)
    i = 0
    while size < PART_ONE_BYTES:
        row = f"P{i:08d},0.07,{i % 2},{(i % 2) * 250000},G{i % 5}\n".encode()
        rows.append(row)
        size += len(row)
        i += 1
    body = header + b"".join(rows)
    # S3 joins the parts byte for byte; the split at 5 MiB may fall inside a row, which
    # is fine because ingestion reads the joined object.
    body += b"".join(
        f"P{j:08d},0.07,{j % 2},{(j % 2) * 250000},G{j % 5}\n".encode() for j in range(i, i + 50)
    )
    return body


@pytest.fixture(scope="module")
def io_worker(request: pytest.FixtureRequest) -> Iterator[subprocess.Popen[bytes]]:
    """`celery -A app.worker.entrypoint worker --queues io`, a process of its own."""
    from backend.tests.conftest_db import test_blob_bucket, test_database_url

    settings = Settings()
    try:
        import redis

        client = redis.Redis.from_url(settings.redis_url.get_secret_value())
        client.ping()
    except Exception as exc:
        # A fail, not a skip: a skipped worker test reads as a pass (the maintainer (by
        # delegation) 09:53:28 BST; lead ruling 10:15:52 BST, endorsed at 10:16:17 BST).
        pytest.fail(f"Redis not reachable, so the io worker cannot start: {type(exc).__name__}")
    client.delete("io")
    env = {
        **os.environ,
        "GIP_DATABASE_URL": test_database_url(),
        "GIP_BLOB_BUCKET": test_blob_bucket(),
    }
    argv = [
        sys.executable, "-m", "celery", "-A", "app.worker.entrypoint", "worker",
        "--queues", "io", "--pool", "solo", "--concurrency", "1", "--loglevel", "INFO",
    ]  # fmt: skip
    log = Path(os.environ.get("TMPDIR", "/tmp")) / f"io-worker-{os.getpid()}.log"
    with log.open("wb") as sink:
        process = subprocess.Popen(argv, env=env, stdout=sink, stderr=subprocess.STDOUT)
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            if process.poll() is not None:
                pytest.fail(f"the io worker exited early: {log.read_text()[-2000:]}")
            if b"ready." in log.read_bytes():
                break
            time.sleep(0.5)
        else:
            process.terminate()
            pytest.fail(f"the io worker never reported ready: {log.read_text()[-2000:]}")
        yield process
        process.terminate()
        process.wait(timeout=30)


@pytest_asyncio.fixture
async def writer(workspace_id, principal, grant) -> dict[str, str]:
    await grant("analyst")
    return {DEV_PRINCIPAL_HEADER: str(principal.id), "Workspace-Id": str(workspace_id)}


async def _wait_for_job(
    client: TestClient, headers: dict[str, str], database: Database, job_id: str
) -> dict:
    """Relay the outbox and poll the Job until it stops being `queued` or `running`."""
    publisher = CeleryPublisher(build_celery(Settings()))
    deadline = time.monotonic() + 90
    body: dict = {}
    while time.monotonic() < deadline:
        await outbox.relay_once(database, publisher)
        body = client.get(f"/api/v1/jobs/{job_id}", headers=headers).json()
        if body["status"] not in {"queued", "running"}:
            return body
        await asyncio.sleep(0.5)
    return body


@pytest.mark.req("FR-421")
@pytest.mark.req("FR-27")
async def test_a_file_uploaded_through_the_public_api_ingests_to_a_succeeded_version(
    api_client: TestClient, io_worker, database: Database, writer: dict[str, str]
) -> None:
    slug = f"up-{hashlib.sha256(os.urandom(8)).hexdigest()[:8]}"
    created = api_client.post("/api/v1/datasets", json={"slug": slug}, headers=writer)
    assert created.status_code == 201, created.text

    csv_bytes = _csv()
    parts = [csv_bytes[:PART_ONE_BYTES], csv_bytes[PART_ONE_BYTES:]]
    response = api_client.post(
        "/api/v1/blobs/upload-url", json={"media_type": "text/csv", "parts": 2}, headers=writer
    )
    assert response.status_code == 200, response.text
    upload = response.json()
    upload_id = upload["id"]
    for url, part in zip(upload["urls"], parts, strict=True):
        put = httpx.put(url, content=part, timeout=60)
        assert put.status_code == 200, put.text

    complete = api_client.post(f"/api/v1/blobs/uploads/{upload_id}/complete", headers=writer)
    assert complete.status_code == 202, complete.text
    promoted = await _wait_for_job(api_client, writer, database, complete.json()["id"])
    digest = hashlib.sha256(csv_bytes).hexdigest()
    assert promoted["queue"] == "io"
    assert promoted["status"] == "succeeded", promoted
    assert promoted["result"] == {"kind": "blob", "ref": digest}

    started = api_client.post(
        f"/api/v1/datasets/{slug}/versions",
        json={"blob": digest, "filename": "upload.csv"},
        headers=writer,
    )
    assert started.status_code == 202, started.text
    ingested = await _wait_for_job(api_client, writer, database, started.json()["id"])
    assert ingested["queue"] == "io"
    assert ingested["status"] == "succeeded", ingested
    assert ingested["result"]["ref"].startswith("dataset_version:")

    version = api_client.get(f"/api/v1/datasets/{slug}/versions/1", headers=writer)
    assert version.json()["status"] == "draft"
