"""The compose path, running (WK-674 Slice 4; PL-1237 Acceptance 12): NFR-534 and NFR-531.

Builds images and starts containers, so it runs only when `GIP_DEPLOY_TESTS=1` is set and only
in a window the lead grants (the build is heavy and the stack publishes a port). The shape
those proofs rely on is held, without Docker, by `test_deploy_stack.py`.

    GIP_DEPLOY_TESTS=1 GIP_N_SHA=<slice head> GIP_N1_SHA=<the commit before it> \\
        uv run pytest -q backend/tests/test_deploy_stack_runtime.py

Each image is built from a `git archive` of its own commit, so **N-1 and N are two images from
two commits** (Acceptance 12), tagged by SHA; both SHAs are printed for the ledger.
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
import os
import pathlib
import re
import subprocess
import tempfile
import threading
import time
import urllib.request
from collections.abc import Iterator
from typing import Any
from uuid import UUID

import pytest
from sqlalchemy import select

ROOT = pathlib.Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.skipif(
    os.environ.get("GIP_DEPLOY_TESTS") != "1", reason="runtime deploy test: set GIP_DEPLOY_TESTS=1"
)
LB_PORT = os.environ.get("GIP_LB_PORT", "18000")
PROJECT = "gip-s4-runtime"


def _compose(sha: str, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "GIP_BUILD": sha, "GIP_LB_PORT": LB_PORT}
    return subprocess.run(
        ["docker", "compose", "-p", PROJECT,
         "-f", str(ROOT / "deploy" / "docker-compose.yml"),
         "-f", str(ROOT / "deploy" / "docker-compose.isolated.yml"),
         "--profile", "app", *args],
        env=env, check=check, capture_output=True, text=True,
    )


def _build_from_commit(sha: str) -> None:
    """Build `gi-pricing-app:<sha>` from `git archive <sha>`, so the image is that commit's."""
    with tempfile.TemporaryDirectory() as tmp:
        archive = subprocess.run(
            ["git", "-C", str(ROOT), "archive", sha], check=True, capture_output=True
        ).stdout
        subprocess.run(["tar", "-x", "-C", tmp], input=archive, check=True)
        subprocess.run(
            ["docker", "build", "-f", "deploy/Dockerfile", "--build-arg", f"GIP_BUILD={sha}",
             "-t", f"gi-pricing-app:{sha}", "."],
            cwd=tmp, check=True,
        )


def _get(path: str) -> int:
    with urllib.request.urlopen(f"http://127.0.0.1:{LB_PORT}{path}", timeout=5) as response:
        return int(response.status)


def _bench() -> Any:
    spec = importlib.util.spec_from_file_location(
        "bench_deploy_path", ROOT / "scripts" / "bench-deploy-path.py"
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _mapped(service: str, port: int) -> str:
    out = _compose(os.environ["GIP_N_SHA"], "port", service, str(port)).stdout.strip()
    return out.rsplit(":", 1)[-1]


@pytest.fixture
def shas() -> tuple[str, str]:
    n = os.environ["GIP_N_SHA"]
    n1 = os.environ["GIP_N1_SHA"]
    print(f"N-1={n1} N={n}")
    for sha in (n1, n):
        _build_from_commit(sha)
    return n1, n


@pytest.fixture
def down() -> Iterator[None]:
    yield
    _compose(os.environ["GIP_N_SHA"], "down", "-v", "--remove-orphans", check=False)


def _seeded_scoring_request() -> tuple[str, dict[str, str], dict[str, Any]]:
    harness = _bench()
    rating = harness._bench_rating()
    dsn = (
        "postgresql+asyncpg://gipricing:gipricing@127.0.0.1:"
        f"{_mapped('postgres', 5432)}/gipricing"
    )
    bundle = asyncio.run(
        rating._serialisable(with_gbm=False, n_expr=rating.N_EXPR_STEPS, rounds=300, rows=5_000)
    )
    workspace_id, api_key = asyncio.run(
        rating._seed(
            bundle, dsn=dsn, bucket="gip-blobs",
            blob_endpoint_url=f"http://127.0.0.1:{_mapped('minio', 9000)}",
        )
    )
    headers = {"X-API-Key": api_key, "Workspace-Id": workspace_id}
    return f"http://127.0.0.1:{LB_PORT}/api/v1/score", headers, json.loads(
        rating._ctx().model_dump_json()
    )


def _score(url: str, headers: dict[str, str], body: dict[str, Any]) -> int:
    request = urllib.request.Request(
        url, data=json.dumps(body).encode(), headers={**headers, "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return int(response.status)


@pytest.mark.req("NFR-534")
@pytest.mark.req("FR-434")
def test_the_scoring_api_runs_and_scores_with_no_worker_service(
    shas: tuple[str, str], down: None
) -> None:
    _, n = shas
    _compose(n, "up", "-d", "--wait", "lb")  # api via lb's dependency; `worker` is never named
    running = _compose(n, "ps", "--status", "running", "--format", "{{.Service}}").stdout.split()
    assert "api" in running
    assert not [s for s in running if s.startswith("worker")]
    assert _get("/readyz") == 200
    url, headers, body = _seeded_scoring_request()
    assert _score(url, headers, body) == 200


@pytest.mark.req("NFR-531")
@pytest.mark.req("FR-435")
def test_previous_version_serves_the_migrated_schema_and_rolls_forward_with_no_failures(
    shas: tuple[str, str], down: None
) -> None:
    n1, n = shas
    # 1. Serve N-1 against the old schema (N-1's own migrate step).
    _compose(n1, "up", "-d", "--wait", "--scale", "api=2", "lb")
    url, headers, body = _seeded_scoring_request()
    assert _score(url, headers, body) == 200
    # 2. Run N's migration as its own step. 3. N-1 still serves against the migrated schema.
    _compose(n, "run", "--rm", "--no-deps", "migrate")
    assert _score(url, headers, body) == 200
    # 4. Roll the api replicas from N-1 to N under load, counting failed requests.
    failures = 0
    stop = threading.Event()

    def load() -> None:
        nonlocal failures
        while not stop.is_set():
            try:
                _score(url, headers, body)
            except Exception:
                failures += 1
            time.sleep(0.02)

    thread = threading.Thread(target=load)
    thread.start()
    try:
        _compose(n, "up", "-d", "--wait", "--no-deps", "--scale", "api=2", "api")
    finally:
        stop.set()
        thread.join()
    assert failures == 0, f"{failures} failed requests while rolling {n1} to {n}"
    assert _score(url, headers, body) == 200


# -- PL-1690 E4.3: delivery, not declaration -------------------------------------------------

#: The bound inside which a submitted Job must leave `queued`: NFR-527's 5 s submit-to-running
#: floor (the relay ticks every second) plus the time to run a cheap, failing-or-succeeding
#: compile. The bound and the elapsed time are quoted in the slice's LG-.
JOB_TERMINAL_BOUND_SECONDS = 60
_TERMINAL = {"succeeded", "failed", "cancelled"}


@pytest.fixture
def built_n() -> str:
    """Only image N: the delivery proof does not need N-1."""
    n = os.environ["GIP_N_SHA"]
    _build_from_commit(n)
    return n


@pytest.fixture
def beat_fixture(built_n: str) -> Iterator[None]:
    """Beat as a one-off TEST FIXTURE from the slice's image, not a compose service (SL-1689's).

    The outbox relay is a beat schedule entry (`app.worker.entrypoint`), so without a beat
    process no Job ever leaves the outbox. It is stopped in teardown.
    """
    started = _compose(
        built_n, "run", "--rm", "-d", "worker-default",
        "celery", "-A", "app.worker.entrypoint", "beat", "--schedule", "/tmp/celerybeat-schedule",
    )
    container = started.stdout.strip().splitlines()[-1]
    try:
        yield
    finally:
        subprocess.run(["docker", "rm", "-f", container], check=False, capture_output=True)


def _api(method: str, path: str, headers: dict[str, str], body: Any = None) -> Any:
    request = urllib.request.Request(
        f"http://127.0.0.1:{LB_PORT}{path}",
        data=None if body is None else json.dumps(body).encode(),
        headers={**headers, "Content-Type": "application/json"},
        method=method,
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read())


@pytest.mark.req("FR-415")
@pytest.mark.req("FR-406")
def test_a_submitted_job_reaches_a_terminal_state_through_the_compose_worker(
    built_n: str, down: None, beat_fixture: None
) -> None:
    """A shape test proves `--queues default,compute` is declared; this proves it is delivered.

    The Job is `rating.compile` (queue `default`, `platform/jobs.py` `DEFAULT_QUEUE_FOR_KIND`):
    the one cheap kind whose own queue is the one a `compute`-only worker does not consume.
    The relay that moves it out of the outbox also rides `default`, so both queues are on the
    path. Red cause: with the worker on `--queues compute` only, the Job stays `queued` past
    the bound.
    """
    n = built_n
    _compose(n, "up", "-d", "--wait", "lb", *_worker_services(n))
    # Seed a workspace, a draft rating version and a key; the bench seed grants the key only
    # `score:execute`, so widen it to what this route and the Job read need.
    _, headers, _ = _seeded_scoring_request()
    _compose(
        n, "exec", "-T", "postgres", "psql", "-U", "gipricing", "-d", "gipricing", "-c",
        "UPDATE service_accounts SET permissions = "
        "'[\"score:execute\", \"rating:read\", \"rating:compile\", \"job:read\"]'::jsonb",
    )
    version_id = _api("GET", "/api/v1/rating-versions", headers)[0]["id"]
    started = time.monotonic()
    job = _api("POST", f"/api/v1/rating-versions/{version_id}/compile", headers)
    assert job["queue"] == "default"
    current = job
    deadline = started + JOB_TERMINAL_BOUND_SECONDS
    while current["status"] not in _TERMINAL and time.monotonic() < deadline:
        time.sleep(1)
        current = _api("GET", f"/api/v1/jobs/{job['id']}", headers)
    status = current["status"]
    elapsed = time.monotonic() - started
    print(f"job {job['id']} kind={job['kind']} queue={job['queue']} -> {status} in {elapsed:.1f}s")
    # `succeeded`, not merely terminal: `failed` is terminal too (the maintainer's (by delegation)
    # entries "2026-10-14 10:13:50 BST", "10:36:42 BST" and "11:43:57 BST" item 2).
    assert status == "succeeded", (
        f"job {job['id']} is {status!r} after {JOB_TERMINAL_BOUND_SECONDS}s: "
        + ("never consumed" if status == "queued" else "ran and did not succeed")
    )
    # The compiled Bundle's content hash, as the rating version's read exposes it
    # (`RatingVersion.bundle.content_hash`; the maintainer's (by delegation) 11:43:57 entry, item 2),
    # and the Job's persisted result ref (the stored blob).
    compiled = _api("GET", f"/api/v1/rating-versions/{version_id}", headers)
    content_hash = (compiled.get("bundle") or {}).get("content_hash", "")
    assert re.fullmatch(r"sha256:[a-f0-9]{64}", content_hash), f"no compiled-bundle hash: {compiled!r}"
    assert (current.get("result") or {}).get("ref"), f"no compiled-bundle ref on {current!r}"


# -- PL-8022 E4.3 extended: the io and scoring pools, asserting `succeeded` -------------------
#
# Run once in S4's build window (the gate does not set GIP_DEPLOY_TESTS), with the whole stack:
#   GIP_DEPLOY_TESTS=1 GIP_N_SHA=<S4 head> GIP_N1_SHA=<S4 head's parent> \
#     uv run pytest -q backend/tests/test_deploy_stack_runtime.py \
#     -k "dataset_ingest or score_batch or sampled_trace or terminal_state"
# NOT RUN at the red-first prep: no services were started (SL-1258 prep).
#
# `succeeded`, not "terminal": `failed` is terminal, and a Job whose kind has no handler goes
# `failed` through a real worker without ever running (PL-8022 P5; the maintainer's
# (by delegation) entry "2026-10-14 10:36:42 BST").

#: Per-test bounds, beside JOB_TERMINAL_BOUND_SECONDS; the elapsed time is printed.
INGEST_BOUND_SECONDS = 90
SCORE_BATCH_BOUND_SECONDS = 90
TRACE_BOUND_SECONDS = 60

_ALL_PERMISSIONS = (
    '["score:execute", "score:batch", "rating:read", "rating:compile", "job:read", '
    '"dataset:read", "dataset:write"]'
)


def _wait_succeeded(job: dict[str, Any], headers: dict[str, str], bound: int) -> dict[str, Any]:
    """Poll the Job to a terminal status or the bound, then assert it `succeeded`."""
    started = time.monotonic()
    current = job
    while current["status"] not in _TERMINAL and time.monotonic() < started + bound:
        time.sleep(1)
        current = _api("GET", f"/api/v1/jobs/{job['id']}", headers)
    elapsed = time.monotonic() - started
    status = current["status"]
    error = (current.get("error") or {}).get("code")
    print(
        f"job {job['id']} kind={job['kind']} queue={job['queue']} -> {status} in {elapsed:.1f}s "
        f"(bound {bound}s)"
    )
    assert status == "succeeded", (
        f"job {job['id']} ({job['kind']}, queue {job['queue']}) is {status!r} after "
        f"{bound}s: " + ("never consumed" if status == "queued" else f"error {error}")
    )
    return current


def _stack_with_seeded_workspace(n: str) -> tuple[str, dict[str, str]]:
    """Bring up lb and every worker service; seed the bench rating version and a key whose
    permissions cover these routes. Returns `(workspace_id, headers)`."""
    _compose(n, "up", "-d", "--wait", "lb", *_worker_services(n))
    _, headers, _ = _seeded_scoring_request()
    _compose(
        n, "exec", "-T", "postgres", "psql", "-U", "gipricing", "-d", "gipricing", "-c",
        f"UPDATE service_accounts SET permissions = '{_ALL_PERMISSIONS}'::jsonb",
    )
    return headers["Workspace-Id"], headers


def _worker_services(n: str) -> list[str]:
    """Every compose service that runs a celery worker (DP-Q1 (b): one per pool), read from
    `config`, so the test starts whatever the compose file declares and names no pool."""
    config = json.loads(_compose(n, "config", "--format", "json").stdout)
    return sorted(
        name for name, svc in config["services"].items()
        if "celery" in (svc.get("command") or []) and "worker" in (svc.get("command") or [])
    )


def _seed_blob_inputs(workspace_id: str, csv: bytes, frame_parquet: bytes) -> tuple[str, str]:
    """Seed, by the backend's own models (psql-equivalent seeding, to be replaced by the public
    upload path in SL 8026): a Dataset Version that makes the CSV blob readable by the workspace
    (`blob_readable_by`), and one that carries the scoring table. Returns `(csv_sha, dv_id)`."""
    harness = _bench()
    rating = harness._bench_rating()
    rating._backend_on_path()
    from pydantic import SecretStr

    from app.config import Environment, Settings
    from app.db.models import DatasetVersionRow
    from app.db.session import Database
    from app.platform.blobs import BlobStore
    from model_schema import new_uuid7

    settings = Settings(
        environment=Environment.LOCAL,
        version="bench",
        database_url=SecretStr(
            "postgresql+asyncpg://gipricing:gipricing@127.0.0.1:"
            f"{_mapped('postgres', 5432)}/gipricing"
        ),
        blob_bucket="gip-blobs",
        blob_endpoint_url=f"http://127.0.0.1:{_mapped('minio', 9000)}",
    )

    async def seed() -> tuple[str, str]:
        database, blobs = Database(settings), BlobStore(settings)
        try:
            async with database.unit_of_work() as session:
                csv_ref = await blobs.put(session, csv, "text/csv")
                frame_ref = await blobs.put(session, frame_parquet, "application/x-parquet")
                for slug, version, sha, name in (
                    ("e43-ingest-seed", 1, csv_ref.sha256, "source"),
                    ("e43-batch-frame", 1, frame_ref.sha256, "scoring_frame"),
                ):
                    session.add(DatasetVersionRow(
                        slug=slug, workspace_id=UUID(workspace_id), dataset_id=new_uuid7(),
                        version=version, status="draft", created_by=new_uuid7(), currency="GBP",
                        tables=[{"name": name, "blob": {"sha256": sha}}],
                    ))
                await session.flush()
                row = (await session.execute(
                    select(DatasetVersionRow.id).where(DatasetVersionRow.slug == "e43-batch-frame")
                )).scalar_one()
            return csv_ref.sha256, str(row)
        finally:
            await database.dispose()

    return asyncio.run(seed())


@pytest.mark.req("FR-415")
@pytest.mark.req("FR-406")
def test_a_dataset_ingest_job_succeeds_through_the_compose_io_worker(
    built_n: str, down: None, beat_fixture: None
) -> None:
    """`dataset.ingest` routes to `io` and must reach `succeeded` through the compose io worker.

    SEEDED, TO BE CONVERTED (the maintainer's (by delegation) entry "2026-10-14 11:10:26 BST"):
    the CSV blob is made readable by a seeded Dataset Version instead of the public upload path.
    The conversion to upload-url -> PUT -> complete -> POST versions, with no seeding, is an
    acceptance line of SL-1722 (the conversion itself is SL-1258's, LG-9810). Red cause: a worker that does not consume `io` leaves the Job
    `queued`.
    """
    workspace_id, headers = _stack_with_seeded_workspace(built_n)
    csv = b"policy_id,exposure,claim_count\nP1,1.0,0\nP2,0.5,1\nP3,1.0,0\n"
    csv_sha, _ = _seed_blob_inputs(workspace_id, csv, b"PAR1")
    _api("POST", "/api/v1/datasets", headers, {"slug": "e43-ingest", "currency": "GBP"})
    job = _api(
        "POST", "/api/v1/datasets/e43-ingest/versions", headers,
        {"blob": csv_sha, "filename": "e43.csv"},
    )
    assert job["queue"] == "io"
    _wait_succeeded(job, headers, INGEST_BOUND_SECONDS)


@pytest.mark.req("FR-415")
@pytest.mark.req("FR-406")
def test_a_score_batch_job_succeeds_through_the_compose_scoring_worker(
    built_n: str, down: None, beat_fixture: None
) -> None:
    """`score.batch` routes to `scoring` and must reach `succeeded`, not merely be consumed.

    A REAL compiled bundle (the bench rating version: real GLM factors) and a real scoring table
    whose columns are `03` section 4.8's reserved four plus the bundle's inputs. Red cause: a
    worker that does not consume `scoring` leaves the Job `queued`; a probe with empty
    parameters was consumed and failed `JOB_HANDLER_FAILED`, which this assert refuses.
    """
    import io

    import polars as pl

    harness = _bench()
    rating = harness._bench_rating()
    workspace_id, headers = _stack_with_seeded_workspace(built_n)
    ctx = json.loads(rating._ctx().model_dump_json())
    rows = 20
    frame = pl.DataFrame({
        "quote_id": [f"Q{i:03d}" for i in range(rows)],
        "purpose": ["new_business"] * rows,
        "effective_date": [ctx["effective_date"]] * rows,
        "rating_version_ref": ["rating_version:placeholder@0"] * rows,
        **{name: [value] * rows for name, value in ctx["inputs"].items()},
    })
    buffer = io.BytesIO()
    frame.write_parquet(buffer, compression="zstd")
    _, dataset_version_id = _seed_blob_inputs(workspace_id, b"x\n", buffer.getvalue())
    ref = str(rating._RATING_VERSION_REF)
    job = _api(
        "POST", "/api/v1/score/batch", headers,
        {"dataset_version_id": dataset_version_id, "rating_version_refs": [ref],
         "table_name": "scoring_frame"},
    )
    assert job["queue"] == "scoring"
    _wait_succeeded(job, headers, SCORE_BATCH_BOUND_SECONDS)


@pytest.mark.req("FR-415")
@pytest.mark.req("FR-406")
def test_a_sampled_trace_is_produced_through_the_compose_scoring_worker(
    built_n: str, down: None, beat_fixture: None
) -> None:
    """A sampled quote's `score.trace_produce` Job succeeds and the trace is listed with a body.

    Sampled with certainty by raising the workspace's `rating.trace_sample_rate` to 1 (the
    seeded version declines nothing; the executor confirms the settings key and the row shape at
    the GO). Two red causes: `scoring` unconsumed (`queued`, "never consumed"), and the handler
    unregistered (`failed`, `JOB_HANDLER_NOT_REGISTERED`, no trace row).
    """
    workspace_id, headers = _stack_with_seeded_workspace(built_n)
    _compose(
        built_n, "exec", "-T", "postgres", "psql", "-U", "gipricing", "-d", "gipricing", "-c",
        "INSERT INTO workspace_settings (id, workspace_id, key, value) "
        f"VALUES (gen_random_uuid(), '{workspace_id}', 'rating.trace_sample_rate', '1.0'::jsonb)",
    )
    harness = _bench()
    ctx = json.loads(harness._bench_rating()._ctx().model_dump_json())
    quote = _api("POST", "/api/v1/score", headers, ctx)
    quote_id = quote.get("quote_id") or ctx["quote_id"]
    jobs = _api("GET", "/api/v1/jobs?kind=score.trace_produce", headers)["items"]
    assert jobs, "scoring a sampled quote submitted no score.trace_produce Job"
    _wait_succeeded(jobs[0], headers, TRACE_BOUND_SECONDS)
    rows = [
        r for r in _api("GET", "/api/v1/traces", headers)["items"] if r["quote_id"] == quote_id
    ]
    message = f"no complete trace with a body for quote {quote_id}: {rows!r}"
    assert rows, message
    assert rows[0]["status"] == "complete", message
    assert rows[0]["trace"], message
