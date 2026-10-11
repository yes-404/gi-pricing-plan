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
