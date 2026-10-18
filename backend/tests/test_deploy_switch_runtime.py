"""The deployment switch on the compose path, running (WK-674 Slice 5; PL-1766 D5.11, D5.14).

**UNPROVEN until the SOLO gate**: it needs the compose stack up from `tools-main` (common rule 20),
and no stack was run for it. It runs only with `GIP_DEPLOY_TESTS=1`, against a stack that is
already up, with `GIP_N_SHA` naming its build:

    GIP_DEPLOY_TESTS=1 GIP_N_SHA=<head> uv run pytest -q backend/tests/test_deploy_switch_runtime.py

S5's runtime tests live in this new module, importing Slice 4's seeding helpers by public name
from `deploy_stack_helpers` (DP-S5-Q8 (a)). The Rating Version is seeded through the services and
deployed through the route; no row is written directly (D5.11).
"""

from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.request
from typing import Any

import pytest
from backend.tests.deploy_stack_helpers import LB_PORT, PROJECT, api, governed_workspace

pytestmark = pytest.mark.skipif(
    os.environ.get("GIP_DEPLOY_TESTS") != "1", reason="runtime deploy test: set GIP_DEPLOY_TESTS=1"
)
COMPILE_BOUND_SECONDS = 120


def _api_containers() -> set[str]:
    out = subprocess.run(
        [
            "docker", "ps", "-q",
            "--filter", f"label=com.docker.compose.project={PROJECT}",
            "--filter", "label=com.docker.compose.service=api",
        ],
        check=True, capture_output=True, text=True,
    ).stdout  # fmt: skip
    return set(out.split())


def _wait_succeeded(job: dict[str, Any], headers: dict[str, str]) -> None:
    deadline = time.monotonic() + COMPILE_BOUND_SECONDS
    while time.monotonic() < deadline:
        current = api("GET", f"/api/v1/jobs/{job['id']}", headers)
        if current["status"] == "succeeded":
            return
        assert current["status"] not in {"failed", "cancelled"}, current
        time.sleep(1)
    raise AssertionError(f"compile job {job['id']} did not succeed in {COMPILE_BOUND_SECONDS}s")


def test_a_deploy_switches_every_api_process_and_a_default_live_quote_is_served() -> None:
    ws = governed_workspace(approved=True)
    analyst, deployer = ws.users["analyst"], ws.users["deployer"]
    _wait_succeeded(
        api("POST", f"/api/v1/rating-versions/{ws.rating_version_id}/compile", analyst), analyst
    )
    done: dict[str, Any] = {}
    for environment in ("dev", "uat"):  # the promotion order
        done = api(
            "POST",
            f"/api/v1/environments/{environment}/deployments",
            deployer,
            {"rating_version_ref": ws.rating_version_ref, "reason": "D5.11"},
        )
    switch = done["switch"]
    containers = _api_containers()
    assert containers, "no api container is running for this project"
    # "Every replica switched" means every process of every container (DP-S5-Q2): each api
    # container appears, and every named process committed.
    assert {name.split(":")[0] for name in switch["processes"]} == {c[:12] for c in containers}
    assert set(switch["processes"].values()) == {"committed"}, switch
    assert switch["receivers"] == len(switch["processes"])

    quote = {k: v for k, v in ws.quote.items() if k != "options"}  # no rating_version_ref
    request = urllib.request.Request(
        f"http://127.0.0.1:{LB_PORT}/api/v1/score",
        data=json.dumps(quote).encode(),
        headers={**ws.headers, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        scored = json.loads(response.read())
    assert response.status == 200
    assert scored["bundle_hash"] == done["bundle_hash"]
