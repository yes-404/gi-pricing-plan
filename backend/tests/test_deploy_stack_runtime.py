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
import hashlib
import json
import os
import pathlib
import re
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import pytest

# PL-1766 D5.14: Slice 4's helpers live in `deploy_stack_helpers` (public names); this module keeps
# its own private names for them so its tests read as they did.
from backend.tests.deploy_stack_helpers import (
    BATCH_PERMISSIONS as _BATCH_PERMISSIONS,
)
from backend.tests.deploy_stack_helpers import (
    LB_PORT,
    PROJECT,
    ROOT,
    _build_from_commit,
    beat_fixture,  # noqa: F401  (pytest fixture, used by name)
    built_n,  # noqa: F401  (pytest fixture, used by name)
)
from backend.tests.deploy_stack_helpers import (
    SCORING_PERMISSIONS as _SCORING_PERMISSIONS,
)
from backend.tests.deploy_stack_helpers import (
    Workspace as _Workspace,
)
from backend.tests.deploy_stack_helpers import (
    api as _api,
)
from backend.tests.deploy_stack_helpers import (
    compose as _compose,
)
from backend.tests.deploy_stack_helpers import (
    compose_settings as _compose_settings,
)
from backend.tests.deploy_stack_helpers import (
    governed_workspace as _governed_workspace,
)
from backend.tests.deploy_stack_helpers import (
    mapped as _mapped,
)
from backend.tests.deploy_stack_helpers import (
    scoring_request as _scoring_request,
)
from sqlalchemy import select

pytestmark = pytest.mark.skipif(
    os.environ.get("GIP_DEPLOY_TESTS") != "1", reason="runtime deploy test: set GIP_DEPLOY_TESTS=1"
)


def _get(path: str) -> int:
    with urllib.request.urlopen(f"http://127.0.0.1:{LB_PORT}{path}", timeout=5) as response:
        return int(response.status)


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
    url, headers, body = _scoring_request()
    assert _score(url, headers, body) == 200


def _api_containers(*, healthy_only: bool = False) -> list[str]:
    """Ids of the running `api` containers of the test project (optionally only healthy ones)."""
    filters = [
        f"label=com.docker.compose.project={PROJECT}",
        "label=com.docker.compose.service=api",
    ]
    if healthy_only:
        filters.append("health=healthy")
    out = subprocess.run(
        ["docker", "ps", "-q", *(a for f in filters for a in ("--filter", f))],
        check=True, capture_output=True, text=True,
    ).stdout
    return out.split()


def _roll_api(sha: str, *, timeout: float = 180.0) -> list[tuple[str, str]]:
    """Run `deploy/roll-api.sh` (SL-1258) and return its step lines as (HH:MM:SS.mmm UTC, line).

    The roll itself, and the sequence it runs, live in the script alone; this only calls it.
    """
    result = subprocess.run(
        [str(ROOT / "deploy" / "roll-api.sh"), "-t", str(int(timeout)), PROJECT,
         str(ROOT / "deploy" / "docker-compose.yml"),
         str(ROOT / "deploy" / "docker-compose.isolated.yml")],
        env={**os.environ, "GIP_BUILD": sha, "GIP_LB_PORT": LB_PORT},
        check=True, capture_output=True, text=True,
    )
    steps = []
    for line in result.stdout.splitlines():
        parts = line.split(" ", 2)
        steps.append((parts[1], line))
    return steps


def _utc_now() -> str:
    """Wall-clock UTC to the millisecond, `YYYY-MM-DDTHH:MM:SS.mmm`."""
    return datetime.now(UTC).isoformat(timespec="milliseconds").removesuffix("+00:00")


def _error_class(exc: BaseException) -> str:
    """The failed-request class the permanent record names (to-lead.md 2026-10-18 01:40:16 BST)."""
    if isinstance(exc, urllib.error.HTTPError):
        return f"HTTP status {exc.code}"
    reason = exc.reason if isinstance(exc, urllib.error.URLError) else exc
    if isinstance(reason, ConnectionResetError):
        return "connection reset"
    if isinstance(reason, TimeoutError):
        return "connect timeout" if isinstance(exc, urllib.error.URLError) else "read timeout"
    return f"other: {type(reason).__name__}"


@pytest.mark.req("NFR-531")
@pytest.mark.req("FR-435")
def test_previous_version_serves_the_migrated_schema_and_rolls_forward_with_no_failures(
    shas: tuple[str, str], down: None
) -> None:
    n1, n = shas
    # 1. Serve N-1 against the old schema (N-1's own migrate step).
    _compose(n1, "up", "-d", "--wait", "--scale", "api=2", "lb")
    url, headers, body = _scoring_request()
    assert _score(url, headers, body) == 200
    # 2. Run N's migration as its own step. 3. N-1 still serves against the migrated schema.
    _compose(n, "run", "--rm", "--no-deps", "migrate")
    assert _score(url, headers, body) == 200
    # 4. Roll the api replicas from N-1 to N under load, counting failed requests.
    # One record per failed request: when (UTC, ms), what class of error, and how long it took.
    failures: list[str] = []
    stop = threading.Event()

    def load() -> None:
        while not stop.is_set():
            started = time.monotonic()
            try:
                _score(url, headers, body)
            except Exception as exc:
                elapsed = time.monotonic() - started
                failures.append(f"{_utc_now()} {_error_class(exc)} elapsed={elapsed * 1000:.0f}ms")
            time.sleep(0.02)

    # The overlap: the number of healthy api containers, sampled every 0.1 s across the roll.
    healthy_counts: list[int] = []

    def sample() -> None:
        while not stop.is_set():
            healthy_counts.append(len(_api_containers(healthy_only=True)))
            time.sleep(0.1)

    threads = [threading.Thread(target=load), threading.Thread(target=sample)]
    for t in threads:
        t.start()
    try:
        steps = _roll_api(n)
    finally:
        stop.set()
        for t in threads:
            t.join()
    print(
        f"healthy api replicas across the roll: min={min(healthy_counts, default=0)} "
        f"over {len(healthy_counts)} samples; failed requests={len(failures)}"
    )
    # The roll steps and the failed requests, in time order (both are UTC wall-clock).
    record = sorted(
        steps + [(f.split("T", 1)[1][:12], f"FAILED REQUEST {f}") for f in failures],
        key=lambda entry: entry[0],
    )
    print("\n".join(line for _, line in record))
    assert healthy_counts, "the overlap sampler took no samples"
    assert min(healthy_counts) >= 1, (
        f"no healthy api replica at some instant of the roll: min={min(healthy_counts)}"
    )
    assert not failures, (
        f"{len(failures)} failed requests while rolling {n1} to {n}; the record, in time order:\n"
        + "\n".join(line for _, line in record)
    )
    assert len(_api_containers()) == 2
    assert _score(url, headers, body) == 200


def _api_containers_all_states() -> list[str]:
    """Ids of every `api` container of the test project, running or not (`docker ps -a`)."""
    out = subprocess.run(
        [
            "docker", "ps", "-a", "-q",
            "--filter", f"label=com.docker.compose.project={PROJECT}",
            "--filter", "label=com.docker.compose.service=api",
        ],
        check=True, capture_output=True, text=True,
    ).stdout
    return out.split()


@pytest.mark.req("NFR-531")
def test_a_failed_api_roll_leaves_the_pre_roll_replicas_and_no_never_healthy_one(
    shas: tuple[str, str], down: None, tmp_path: pathlib.Path
) -> None:
    """FD-1804: a roll whose new replicas never pass their healthcheck, before the old ones are
    stopped, returns the project to its pre-roll replicas (PL-1812; the maintainer's (by
    delegation) entry "2026-10-18 03:11:40 BST", item 3). No shipped compose file changes: an
    extra file in `tmp_path` makes the `api` healthcheck always fail, which stands for an image
    whose healthcheck never passes."""
    n1, n = shas
    _compose(n1, "up", "-d", "--wait", "--scale", "api=2", "lb")
    old = sorted(_api_containers())
    assert len(old) == 2
    never_healthy = tmp_path / "docker-compose.never-healthy.yml"
    never_healthy.write_text(
        "services:\n"
        "  api:\n"
        "    healthcheck:\n"
        "      test: [\"CMD-SHELL\", \"exit 1\"]\n"
        "      interval: 2s\n"
        "      timeout: 2s\n"
        "      retries: 1\n"
    )
    result = subprocess.run(
        [
            str(ROOT / "deploy" / "roll-api.sh"), "-t", "30", PROJECT,
            str(ROOT / "deploy" / "docker-compose.yml"),
            str(ROOT / "deploy" / "docker-compose.isolated.yml"),
            str(never_healthy),
        ],
        env={**os.environ, "GIP_BUILD": n, "GIP_LB_PORT": LB_PORT},
        capture_output=True, text=True,
    )
    print(result.stdout, result.stderr)
    assert result.returncode != 0, "the roll must fail when no new replica turns healthy"
    remaining = sorted(_api_containers_all_states())
    assert remaining == old, (
        f"a failed roll must leave exactly the pre-roll api containers {old}, found {remaining}"
    )
    assert sorted(_api_containers(healthy_only=True)) == old
    url, headers, body = _scoring_request()
    statuses = [_score(url, headers, body) for _ in range(20)]
    assert statuses == [200] * 20, f"requests through lb after the failed roll: {statuses}"


# -- PL-1690 E4.3: delivery, not declaration -------------------------------------------------

#: The bound inside which a submitted Job must leave `queued`: NFR-527's 5 s submit-to-running
#: floor (the relay ticks every second) plus the time to run a cheap, failing-or-succeeding
#: compile. The bound and the elapsed time are quoted in the slice's LG-.
JOB_TERMINAL_BOUND_SECONDS = 60
_TERMINAL = {"succeeded", "failed", "cancelled"}


@pytest.mark.req("FR-415")
@pytest.mark.req("FR-406")
def test_a_submitted_job_reaches_a_terminal_state_through_the_compose_worker(
    built_n: str, down: None, beat_fixture: None  # noqa: F811
) -> None:
    """A shape test proves the declared queue list is set; this proves it is delivered.

    The Job is `rating.compile` (queue `default`, `platform/jobs.py` `DEFAULT_QUEUE_FOR_KIND`):
    the one cheap kind whose own queue is the one a `compute`-only worker does not consume.
    The relay that moves it out of the outbox also rides `default`, so both queues are on the
    path. Red cause: with the worker on `--queues compute` only, the Job stays `queued` past
    the bound.
    """
    n = built_n
    _compose(n, "up", "-d", "--wait", "lb", *_worker_services(n))
    # A DRAFT Rating Version created by the services (`create_rating_version`), never by a row
    # write: compile is refused for any other status (409 RATING_VERSION_IMMUTABLE, FR-239), and
    # PL-1690 E4.3 names no status ("one cheap Job"). The caller is the demo `analyst`, a USER
    # principal that really holds `rating:compile`, `rating:read` and `job:read` through its
    # built-in role (the maintainer's (by delegation) entry "2026-10-16 10:31:43 BST", (1b)).
    ws = _governed_workspace(approved=False)
    headers = ws.users["analyst"]
    version_id = ws.rating_version_id
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
    # (`RatingVersion.bundle.content_hash`; the maintainer's (by delegation) 11:43:57 entry,
    # item 2),
    # and the Job's persisted result ref (the stored blob).
    compiled = _api("GET", f"/api/v1/rating-versions/{version_id}", headers)
    content_hash = (compiled.get("bundle") or {}).get("content_hash", "")
    assert re.fullmatch(r"sha256:[a-f0-9]{64}", content_hash), (
        f"no compiled-bundle hash: {compiled!r}"
    )
    assert (current.get("result") or {}).get("ref"), f"no compiled-bundle ref on {current!r}"


#: How long a Job is watched with no `scheduler` running before it is called stuck. The relay
#: ticks every second (`app.worker.entrypoint`), so a Job that was going to leave `queued` has
#: done so well inside this.
NO_SCHEDULER_WATCH_SECONDS = 15


@pytest.mark.req("FR-432")
@pytest.mark.req("FR-406")
@pytest.mark.req("FR-413")
def test_the_scheduler_service_is_what_moves_a_job_out_of_the_outbox(
    built_n: str, down: None  # noqa: F811
) -> None:
    """PL-1688 Task 3: reachable, not only declared; and red with the scheduler stopped.

    The stack comes up with `lb` and every worker and NO `scheduler`: the committed Job must stay
    `queued` (the relay is a beat schedule entry, so nothing moves it; `scripts/demo.py`: "without
    `beat`, committed Jobs stay `queued` and nothing says why"). Then the compose `scheduler`
    service is started and the same Job must reach `succeeded` within `JOB_TERMINAL_BOUND_SECONDS`.
    The same assertion also proves DP-B1 end to end: the relay's task rides `default`, and a
    worker set that did not consume it would leave the Job `queued` here.
    """
    n = built_n
    _compose(n, "up", "-d", "--wait", "lb", *_worker_services(n))
    ws = _governed_workspace(approved=False)
    headers = ws.users["analyst"]
    job = _api("POST", f"/api/v1/rating-versions/{ws.rating_version_id}/compile", headers)
    deadline = time.monotonic() + NO_SCHEDULER_WATCH_SECONDS
    current = job
    while time.monotonic() < deadline:
        time.sleep(1)
        current = _api("GET", f"/api/v1/jobs/{job['id']}", headers)
        assert current["status"] == "queued", (
            f"job {job['id']} left `queued` ({current['status']!r}) with no scheduler running"
        )
    print(f"job {job['id']} stayed queued for {NO_SCHEDULER_WATCH_SECONDS}s with no scheduler")
    _compose(n, "up", "-d", "--wait", "scheduler")
    started = time.monotonic()
    deadline = started + JOB_TERMINAL_BOUND_SECONDS
    while current["status"] not in _TERMINAL and time.monotonic() < deadline:
        time.sleep(1)
        current = _api("GET", f"/api/v1/jobs/{job['id']}", headers)
    elapsed = time.monotonic() - started
    print(f"job {job['id']} -> {current['status']} {elapsed:.1f}s after the scheduler started")
    assert current["status"] == "succeeded", (
        f"job {job['id']} is {current['status']!r} {JOB_TERMINAL_BOUND_SECONDS}s after the "
        "scheduler started"
    )


# -- PL-8022 E4.3 extended: the io and scoring pools, asserting `succeeded` -------------------
#
# Run once in S4's build window (the gate does not set GIP_DEPLOY_TESTS), with the whole stack:
#   GIP_DEPLOY_TESTS=1 GIP_N_SHA=<S4 head> GIP_N1_SHA=<S4 head's parent> \
#     uv run pytest -q backend/tests/test_deploy_stack_runtime.py \
#     -k "dataset_ingest or score_batch or sampled_trace or terminal_state"
# NOT RUN since the seeds moved onto the governed path (SL-1258, DP-S4-SEED): owed on compose.
#
# `succeeded`, not "terminal": `failed` is terminal, and a Job whose kind has no handler goes
# `failed` through a real worker without ever running (PL-8022 P5; the maintainer's
# (by delegation) entry "2026-10-14 10:36:42 BST").

#: Per-test bounds, beside JOB_TERMINAL_BOUND_SECONDS; the elapsed time is printed.
INGEST_BOUND_SECONDS = 90
SCORE_BATCH_BOUND_SECONDS = 90
TRACE_BOUND_SECONDS = 60


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


def _stack_with_workspace(n: str, scoring: list[str] = _SCORING_PERMISSIONS) -> _Workspace:
    """Bring up lb and every worker service; seed an APPROVED Rating Version through the
    governed path, the scoring key (`scoring` permissions, through the route) and the demo user
    principals' headers (`ws.users`) for every route that is not a scoring route."""
    _compose(n, "up", "-d", "--wait", "lb", *_worker_services(n))
    return _governed_workspace(approved=True, scoring=scoring)


def _worker_services(n: str) -> list[str]:
    """Every compose service that runs a celery worker (DP-Q1 (b): one per pool), read from
    `config`, so the test starts whatever the compose file declares and names no pool."""
    config = json.loads(_compose(n, "config", "--format", "json").stdout)
    return sorted(
        name for name, svc in config["services"].items()
        if "celery" in (svc.get("command") or []) and "worker" in (svc.get("command") or [])
    )


def _put_blob_inputs(workspace_id: str, csv: bytes, frame_parquet: bytes) -> tuple[str, str]:
    """Seed, by the backend's own models (psql-equivalent seeding, to be replaced by the public
    upload path in SL 8026): a Dataset Version that makes the CSV blob readable by the workspace
    (`blob_readable_by`), and one that carries the scoring table. Returns `(csv_sha, dv_id)`."""
    from app.db.models import DatasetVersionRow
    from app.db.session import Database
    from app.platform.blobs import BlobStore
    from model_schema import new_uuid7

    settings = _compose_settings()

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
    built_n: str, down: None, beat_fixture: None  # noqa: F811
) -> None:
    """`dataset.ingest` routes to `io` and must reach `succeeded` through the compose io worker.

    The CSV goes in by the public upload path, with no seeding (PL 8061 E4.8, carried by
    PL-1812 / SL-1813; the maintainer's (by delegation) entry "2026-10-18 03:11:40 BST", DP-E1
    (b)): upload-url -> PUT to the presigned URL -> complete (a `blob.promote` Job on `io`) ->
    POST versions (a `dataset.ingest` Job on `io`). Both Jobs must reach `succeeded` with their
    output asserted. Red cause: a worker that does not consume `io` leaves a Job `queued`.
    """
    ws = _stack_with_workspace(built_n)
    headers = ws.users["analyst"]  # dataset:write, job:read
    csv = b"policy_id,exposure,claim_count\nP1,1.0,0\nP2,0.5,1\nP3,1.0,0\n"
    _api("POST", "/api/v1/datasets", headers, {"slug": "e43-ingest", "currency": "GBP"})
    # One part is enough: the multipart path is SL-1722's R1 to prove; this proves the io worker.
    upload = _api(
        "POST", "/api/v1/blobs/upload-url", headers, {"media_type": "text/csv", "parts": 1}
    )
    # The presigned single-part URL signs the media type, so the PUT sends it; no auth headers.
    # The URL is signed for the compose-internal host (`minio:9000`), which the test process
    # cannot resolve: connect to the published port and send the signed Host header unchanged.
    signed = urllib.parse.urlsplit(upload["urls"][0])
    target = signed._replace(netloc=f"127.0.0.1:{_mapped('minio', 9000)}").geturl()
    put = urllib.request.Request(
        target, data=csv, headers={"Content-Type": "text/csv", "Host": signed.netloc},
        method="PUT",
    )
    with urllib.request.urlopen(put, timeout=60) as response:
        assert response.status == 200
    promote = _api("POST", f"/api/v1/blobs/uploads/{upload['id']}/complete", headers)
    assert promote["queue"] == "io"
    promoted = _wait_succeeded(promote, headers, INGEST_BOUND_SECONDS)
    csv_sha = hashlib.sha256(csv).hexdigest()
    assert promoted["result"] == {"kind": "blob", "ref": csv_sha}
    job = _api(
        "POST", "/api/v1/datasets/e43-ingest/versions", headers,
        {"blob": csv_sha, "filename": "e43.csv"},
    )
    assert job["queue"] == "io"
    ingested = _wait_succeeded(job, headers, INGEST_BOUND_SECONDS)
    assert ingested["result"]["ref"].startswith("dataset_version:")


@pytest.mark.req("FR-415")
@pytest.mark.req("FR-406")
def test_a_score_batch_job_succeeds_through_the_compose_scoring_worker(
    built_n: str, down: None, beat_fixture: None  # noqa: F811
) -> None:
    """`score.batch` routes to `scoring` and must reach `succeeded`, not merely be consumed.

    A REAL compiled bundle (the governed approved Rating Version: the freMTPL2 GLM through
    its seeded rate tables) and a real scoring table whose columns are `03` section 4.8's
    reserved four plus the bundle's inputs. Red cause: a worker that does not consume
    `scoring` leaves the Job `queued`; a probe with empty parameters was consumed and failed
    `JOB_HANDLER_FAILED`, which this assert refuses.
    """
    import io

    import polars as pl

    from app.db.models import BlobRow
    from app.db.session import Database
    from app.platform.blobs import BlobStore, to_ref

    ws = _stack_with_workspace(built_n, _BATCH_PERMISSIONS)
    quote = ws.quote
    rows = 20
    frame = pl.DataFrame({
        "quote_id": [f"Q{i:03d}" for i in range(rows)],
        "purpose": ["new_business"] * rows,
        "effective_date": [quote["effective_date"]] * rows,
        "rating_version_ref": ["rating_version:placeholder@0"] * rows,
        **{name: [value] * rows for name, value in quote["inputs"].items()},
    })
    buffer = io.BytesIO()
    frame.write_parquet(buffer, compression="zstd")
    _, dataset_version_id = _put_blob_inputs(ws.workspace_id, b"x\n", buffer.getvalue())
    job = _api(
        "POST", "/api/v1/score/batch", ws.headers,
        {"dataset_version_id": dataset_version_id, "rating_version_refs": [ws.rating_version_ref],
         "table_name": "scoring_frame"},
    )
    assert job["queue"] == "scoring"
    # The job is read by the demo `analyst` (`job:read`): the scoring key holds scoring only.
    done = _wait_succeeded(job, ws.users["analyst"], SCORE_BATCH_BOUND_SECONDS)

    # `succeeded` is not the proof: the output must hold one row per input row. The expected
    # count is the INPUT's own height, read from the frame sent, never a literal (DP-S4-SEED
    # (a) item 3), so a changed fixture cannot leave this assert passing vacuously.
    expected_rows = frame.height
    assert expected_rows > 0, "the scoring frame is empty: the assert below would be vacuous"
    summary_sha = (done.get("result") or {}).get("ref")
    assert summary_sha, f"no batch summary ref on {done!r}"

    async def read_output() -> tuple[dict[str, Any], pl.DataFrame]:
        settings = _compose_settings()
        database, blobs = Database(settings), BlobStore(settings)
        try:
            async with database.session() as session:
                summary_row = await session.get(BlobRow, summary_sha)
                assert summary_row is not None, f"summary blob {summary_sha} not in the store"
                summary = json.loads(await blobs.read(to_ref(summary_row)))
                (result,) = summary["results"]
                output_sha = result["output_blob_sha256"]
                assert output_sha, f"the batch wrote no output artifact: {result!r}"
                output_row = await session.get(BlobRow, output_sha)
                assert output_row is not None, f"output blob {output_sha} not in the store"
                return result, pl.read_parquet(io.BytesIO(await blobs.read(to_ref(output_row))))
        finally:
            await database.dispose()

    result, output = asyncio.run(read_output())
    print(
        f"batch input rows={expected_rows} output rows={output.height} "
        f"summary row_count={result['row_count']}"
    )
    assert output.height == expected_rows, (
        f"batch output has {output.height} rows for {expected_rows} input rows"
    )
    assert result["row_count"] == expected_rows, result


@pytest.mark.req("FR-415")
@pytest.mark.req("FR-406")
def test_a_sampled_trace_is_produced_through_the_compose_scoring_worker(
    built_n: str, down: None, beat_fixture: None  # noqa: F811
) -> None:
    """A sampled quote's `score.trace_produce` Job succeeds and the trace is listed with a body.

    Sampled with certainty by raising the workspace's `rating.trace_sample_rate` to 1 through
    `PUT /api/v1/settings` (the seeded version declines nothing). Two red causes: `scoring`
    unconsumed (`queued`, "never consumed"), and the handler unregistered
    (`failed`, `JOB_HANDLER_NOT_REGISTERED`, no trace row).
    """
    ws = _stack_with_workspace(built_n)
    # Three principals, each holding what it calls: the demo `admin` (`admin:manage_settings`)
    # sets the rate, the scoring key scores, the demo `analyst` (`job:read`, `rating:read`) reads
    # the Job and the trace (the maintainer's (by delegation) entry "2026-10-16 10:31:43 BST",
    # (1b)).
    admin, headers = ws.users["admin"], ws.users["analyst"]
    # The governed path (SL-1258, DP-S4-SEED-2 (2)): `PUT /api/v1/settings`
    # (`api/settings.py` `update_settings`, `admin:manage_settings`) validates the key against
    # its declaration (`platform/settings.py` `rating.trace_sample_rate`, FLOAT in [0, 1]).
    updated = _api("PUT", "/api/v1/settings", admin, {"values": {"rating.trace_sample_rate": 1.0}})
    resolved = {r["key"]: r for r in updated}["rating.trace_sample_rate"]
    assert resolved["effective_value"] == 1.0, resolved
    ctx = ws.quote
    quote = _api("POST", "/api/v1/score", ws.headers, ctx)
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
