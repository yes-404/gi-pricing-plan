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
import subprocess
import tempfile
import threading
import time
import urllib.request
from collections.abc import Iterator
from typing import Any

import pytest

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
    assert "worker" not in running
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
        built_n, "run", "--rm", "-d", "worker",
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
    _compose(n, "up", "-d", "--wait", "lb", "worker")
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
    status = job["status"]
    deadline = started + JOB_TERMINAL_BOUND_SECONDS
    while status not in _TERMINAL and time.monotonic() < deadline:
        time.sleep(1)
        status = _api("GET", f"/api/v1/jobs/{job['id']}", headers)["status"]
    elapsed = time.monotonic() - started
    print(f"job {job['id']} kind={job['kind']} queue={job['queue']} -> {status} in {elapsed:.1f}s")
    assert status in _TERMINAL, (
        f"job {job['id']} still {status!r} after {JOB_TERMINAL_BOUND_SECONDS}s: "
        "nothing consumed its queue"
    )
