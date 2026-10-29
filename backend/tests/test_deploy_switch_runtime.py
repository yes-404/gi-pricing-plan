"""The deployment switch on the compose path, running (WK-674 Slice 5; PL-1766 D5.11, D5.14).

**Proven 2026-10-29** on the throwaway compose project `gip-s4-runtime` at head
870d08f5ce68c06ef4ba345b55114ca29208e477 (`1 passed in 71.75s`, rc=0, SL-1968's build window;
before that edit it started no stack and left containers up). It needs the compose stack, which
the test starts and tears down, and the built image. It runs only with `GIP_DEPLOY_TESTS=1` and
`GIP_N_SHA` naming the build. The
`built_n` fixture builds that image if it is missing, and the `beat_fixture` fixture starts a
beat for the run:

    GIP_DEPLOY_TESTS=1 GIP_N_SHA=<head> uv run pytest -q backend/tests/test_deploy_switch_runtime.py

S5's runtime tests live in this new module, importing Slice 4's seeding helpers by public name
from `deploy_stack_helpers` (DP-S5-Q8 (a)). The Rating Version is seeded through the services and
deployed through the route; no row is written directly (D5.11). The approval evidence (the
Regression Suite, the regression run, submit, two decisions) goes through the API too, so every
Job runs on the stack's workers; the deployed bundle is the one the route's compile made.

When `GIP_EVIDENCE_DIR` is set, the deployed bundle's bytes are written to
`$GIP_EVIDENCE_DIR/deployed-bundle.json` right after the deploy, before any assert on it.
"""

from __future__ import annotations

import asyncio
import json
import os
import pathlib
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any
from uuid import UUID

import pytest
from backend.tests.deploy_stack_helpers import (
    LB_PORT,
    PROJECT,
    beat_fixture,  # noqa: F401  (pytest fixture, used by name)
    built_n,  # noqa: F401  (pytest fixture, used by name)
    compose_settings,
    governed_workspace,
)
from backend.tests.deploy_stack_helpers import api as _stack_api
from backend.tests.deploy_stack_helpers import (
    compose as _compose,
)
from backend.tests.deploy_stack_helpers import mapped as _mapped
from backend.tests.test_deploy_stack_runtime import (
    _worker_services,
    down,  # noqa: F401  (pytest fixture, used by name)
)

from model_schema import QuoteContext, RegressionSuiteVersionCreate

pytestmark = pytest.mark.skipif(
    os.environ.get("GIP_DEPLOY_TESTS") != "1", reason="runtime deploy test: set GIP_DEPLOY_TESTS=1"
)
COMPILE_BOUND_SECONDS = 120


def api(method: str, path: str, headers: dict[str, str], body: Any = None) -> Any:
    """`deploy_stack_helpers.api`, printing the status and JSON body of any non-2xx response
    before it raises, so a refused call in the SOLO gate names its problem detail."""
    try:
        return _stack_api(method, path, headers, body)
    except urllib.error.HTTPError as error:
        print(f"{method} {path} -> {error.code}: {error.read().decode(errors='replace')}")
        raise


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


def _wait_succeeded(job: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    """The Job once it has `succeeded` with an output: a merely terminal Job is not enough."""
    deadline = time.monotonic() + COMPILE_BOUND_SECONDS
    current = job
    while time.monotonic() < deadline:
        current = api("GET", f"/api/v1/jobs/{job['id']}", headers)
        if current["status"] == "succeeded":
            assert current["result"], current
            assert current["result"]["ref"], current
            return current
        assert current["status"] not in {"failed", "cancelled"}, current
        time.sleep(1)
    raise AssertionError(
        f"compile job {job['id']} did not succeed in {COMPILE_BOUND_SECONDS}s; last seen: "
        f"status={current.get('status')!r} result={current.get('result')!r} "
        f"error={current.get('error')!r} job={current!r}"
    )


def _suite_body(ws: Any) -> dict[str, Any]:
    """The body of `POST /regression-suites/{slug}/versions` for the demo rating version.

    **Mirrors `examples/fremtpl2/model.py:874-894 @ef2f0462`** (`author_demo_rating_evidence`'s
    golden-quote loop and `RegressionSuiteContent` assembly), which cannot be called here: it runs
    its Jobs in the test process, on a worker that is not the stack's (PL-1766 D5.11, the
    maintainer's entry "2026-10-19 03:58:53 BST", option (1)). Nothing is hand-shaped: the cases
    are the example's `demo_golden_cases`, the properties its `declared_properties`, and the body
    is validated as model-schema's `RegressionSuiteVersionCreate`.
    """
    from backend.tests.test_demo_rating_evidence import _BASE_MINOR, _bandings, demo_model
    from sqlalchemy import select

    from app.db.models import ModelRow
    from app.db.session import Database

    workspace_id = ws.workspace_id

    async def cases() -> list[Any]:
        database = Database(compose_settings())
        try:
            async with database.session() as session:
                model_id = (
                    await session.execute(
                        select(ModelRow.id).where(ModelRow.workspace_id == UUID(workspace_id))
                    )
                ).scalar_one()
            _, fit = await demo_model.load_approved_glm(database, UUID(workspace_id), model_id)
            return demo_model.demo_golden_cases(fit, _bandings(), _BASE_MINOR)
        finally:
            await database.dispose()

    golden = []
    for case in asyncio.run(cases()):
        context = QuoteContext.model_validate({
            "purpose": "new_business", "quoted_at": "2026-09-28T09:00:00",
            "effective_date": "2026-10-01", "inputs": case.inputs,
            "options": {"rating_version_ref": ws.rating_version_ref},
        })
        golden.append({
            "name": f"{demo_model.FREMTPL2_ALGORITHM_SLUG}-{case.name}",
            "context": context.model_dump(mode="json", exclude={"options"}),
            "expected": {"payable_premium_minor": case.expected_minor, "outcome": "quoted"},
            "tolerance": {"money_minor": 0},
            "note": f"the approved GLM's premium for {case.name}, computed from its coefficients",
        })
    return RegressionSuiteVersionCreate.model_validate({
        "algorithm_slug": demo_model.FREMTPL2_ALGORITHM_SLUG,
        "golden_quotes": golden,
        "properties": demo_model.declared_properties(),
        "generation": {
            "cases": 25, "seed": demo_model.SPLIT_SEED, "strategy": "input_contract_sampling",
        },
        "change_note": demo_model.DEMO_CHANGE_NOTE,
    }).model_dump(mode="json")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args: Any, **kwargs: Any) -> None:
        return None


def _fetch_blob(sha256: str, headers: dict[str, str]) -> bytes:
    """`GET /api/v1/blobs/{sha256}`: a 307 to a URL signed for the compose-internal host, which the
    test process cannot resolve, so connect to the published port and send the signed Host header
    unchanged (as `test_deploy_stack_runtime.py` does for its upload)."""
    opener = urllib.request.build_opener(_NoRedirect)
    url = f"http://127.0.0.1:{LB_PORT}/api/v1/blobs/{sha256}"
    with pytest.raises(urllib.error.HTTPError) as redirect:
        opener.open(urllib.request.Request(url, headers=headers), timeout=30)
    assert redirect.value.code == 307, redirect.value.code
    signed = urllib.parse.urlsplit(redirect.value.headers["Location"])
    target = signed._replace(netloc=f"127.0.0.1:{_mapped('minio', 9000)}").geturl()
    get = urllib.request.Request(target, headers={"Host": signed.netloc})
    with urllib.request.urlopen(get, timeout=60) as response:
        return response.read()  # type: ignore[no-any-return]


def test_a_deploy_switches_every_api_process_and_a_default_live_quote_is_served(
    built_n: str, down: None, beat_fixture: None  # noqa: F811
) -> None:
    _compose(built_n, "up", "-d", "--wait", "lb", *_worker_services(built_n))
    # `rating.compile` is refused with 409 `RATING_VERSION_IMMUTABLE` unless the version is a
    # draft (FR-239, `require_compilable`), so the route compiles the draft, and the SAME version
    # is then approved (D5.11). The approval evidence goes through the API as well, with no second
    # compile: a second compile would replace the bundle with different bytes (`compiled_at`).
    ws = governed_workspace(approved=False)
    analyst, actuary, deployer = ws.users["analyst"], ws.users["actuary"], ws.users["deployer"]
    rating_path = f"/api/v1/rating-versions/{ws.rating_version_id}"
    compiled = _wait_succeeded(api("POST", f"{rating_path}/compile", analyst), analyst)
    first = api("GET", rating_path, analyst)["bundle"]
    produced = first["blob_sha256"]
    assert produced in compiled["result"]["ref"], (produced, compiled["result"])
    slug = "fremtpl2-rate-suite"  # examples/fremtpl2/model.py DEMO_SUITE_SLUG
    api("POST", f"/api/v1/regression-suites/{slug}/versions", analyst, _suite_body(ws))
    regression = _wait_succeeded(api("POST", f"{rating_path}/regression-runs", analyst), analyst)
    # The regression Job ran on the stack's worker: `platform_build` is `{version}+{build}` and
    # an in-process run says `+local` (`Job.platform_build`, model_schema/jobs.py).
    assert (regression["platform_build"] or "").endswith(f"+{os.environ['GIP_N_SHA']}"), regression
    submitted = api(
        "POST", f"{rating_path}/submit", actuary,
        {"change_summary": "D5.11 deploy switch runtime test"},
    )
    for who in ("approver", "second_approver"):
        api(
            "POST", f"/api/v1/approval-requests/{submitted['approval_request_id']}/decide",
            ws.users[who], {"decision": "approve", "comment": "D5.11"},
        )
    assert api("GET", rating_path, analyst)["status"] == "approved"
    done: dict[str, Any] = {}
    for environment in ("dev", "uat"):  # the promotion order
        done = api(
            "POST",
            f"/api/v1/environments/{environment}/deployments",
            deployer,
            {"rating_version_ref": ws.rating_version_ref, "reason": "D5.11"},
        )
    # The deployment's compiled output is the one the ROUTE's compile Job produced: nothing after
    # it compiles again. The bytes are captured first, so a failing identity assert still leaves
    # the file for the gate (D5.11 (d)). Never loosen the asserts.
    deployed = api("GET", rating_path, analyst)["bundle"]
    evidence_dir = os.environ.get("GIP_EVIDENCE_DIR")
    if evidence_dir:
        (pathlib.Path(evidence_dir) / "deployed-bundle.json").write_bytes(
            _fetch_blob(deployed["blob_sha256"], analyst)
        )
    assert deployed["blob_sha256"] == produced, (deployed, produced)
    assert deployed["content_hash"] == first["content_hash"], (deployed, first)
    assert done["bundle_hash"].removeprefix("sha256:") == deployed["content_hash"].removeprefix(
        "sha256:"
    ), (done["bundle_hash"], deployed)
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
