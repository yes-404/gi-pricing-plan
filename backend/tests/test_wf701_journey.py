"""WF-701 — the deployment steps, walked over HTTP (PL 8014, SL 8015).

`docs/workflows/WF-00701-deploy-and-monitor.md` is the journey this file proves:
`examples/fremtpl2/journey_wf701.py` is an `httpx` client of `/api/v1` that walks the deployment
steps A1 to A6, C1 to C4, C6 and C7, and these tests run it against the app in process, after
`run_wf699_journey` has left its state (the live `rv3` in `dev`, `uat` and `prod`).

A client that returns `ok` for every step proves nothing. So each test asserts a *code* the API
returned, and the end-to-end test reads every effect back through a route the journey did not
use to cause it, from the test, not from the journey's own record.

Authored red-first on `main` (T1 to T4 of PL 8014). A2 and C4 (the switch under a concurrent
stream) and C6's replica limb are T5 and wait for Slice 5; the step-order assertion below
filters them out until T5 removes the filter.

Marker form: `scripts/req-coverage.py` reads only the decorator form of the `req` marker with an
FR or NFR id, so the requirement ids the journey exercises are the markers and `WF-701` is
named here and in the test names (the form of `test_wf699_journey.py`).
"""

from __future__ import annotations

import asyncio
import importlib.util
import sys
from pathlib import Path
from typing import Any
from uuid import UUID

import pytest
from backend.tests.test_wf699_journey import _world

_EXAMPLE = Path(__file__).resolve().parents[2] / "examples" / "fremtpl2"
sys.path.insert(0, str(_EXAMPLE))  # the journeys import their sibling `algorithm`


def _load(name: str, filename: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, _EXAMPLE / filename)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


wf699 = _load("demo_journey", "journey.py")
# Fails at collection while the module does not exist: R1, by its cause.
wf701 = _load("demo_journey_wf701", "journey_wf701.py")

#: PL 8014 T1: the only two lines a WF-701 run may print as a ruled limb. `RL 8019` is a working
#: id until the ruling is minted; the mint replaces it here and in the journey.
COMPOSE_ONLY_LINE = "COMPOSE-ONLY A2/C4/C6 replica limb"
ERRORS_LINE = "C7-errors: refused, not traced (FR-259, RL 8019)"

FIRST_LINE = (
    "WF-701 demo: process environment dev with development identity (dev auth); "
    "deployments target the Environment resources uat and prod"
)

#: T3/T4's order, PL 8014's step table, without A2 and C4 (T5). C3's three limbs and C7's four are
#: separate steps because each asserts a different server effect. `A1dev` is a step the plan's
#: table lacks: `uat` takes a deploy only after the same version is deployed to `dev`
#: (`PROMOTION_ORDER_VIOLATION`, probed on `main` 4420f91f), so A1 cannot be the first deploy.
STEPS_BEFORE_T5 = [
    "C2", "C3i", "A1dev", "A1", "A3", "A4", "A5", "A6", "C3ii", "C3iii", "C1", "C6",
    "C7i", "C7ii", "C7iii", "C7iv",
]  # fmt: skip


@pytest.mark.req("FR-259")
def test_wf701_the_ruled_lines_are_exactly_the_ruled_ones() -> None:
    """PL 8014 T1 and acceptance 2: two ruled lines and no others, and no `KNOWN GAP C7-errors`
    (RL 8019 walked the limb)."""
    assert [entry.line for entry in wf701.RULED_LINES] == [COMPOSE_ONLY_LINE, ERRORS_LINE]
    assert not [e for e in wf701.RULED_LINES if "KNOWN GAP" in e.line]


@pytest.mark.req("FR-259")
def test_wf701_an_unruled_skip_fails_the_journey() -> None:
    """The form of `test_an_unowned_skip_fails_the_journey` (WF-699): a skip line that is not one
    of the two ruled ones fails the journey for that step; a ruled one does not."""
    ruled = wf701.RULED_LINES[0]
    unruled = wf699.Skip(step="X1", line="SKIPPED X1: not built yet")
    wf701.check_ruled_lines([ruled])
    with pytest.raises(wf699.JourneyStepFailed) as failure:
        wf701.check_ruled_lines([ruled, unruled])
    assert failure.value.step == "X1"
    assert str(failure.value).startswith("X1: UNRULED_SKIP")


@pytest.mark.req("FR-259")
def test_wf701_reuses_the_wf699_failure_and_skip_types() -> None:
    """PL 8014 T1: `JourneyStepFailed` and `Skip` are imported from `journey.py`, not defined a
    second time, so the demo command catches one exception type for both journeys."""
    assert wf701.JourneyStepFailed is wf699.JourneyStepFailed
    assert wf701.Skip is wf699.Skip


def _run(coro: Any) -> Any:
    return asyncio.get_event_loop().run_until_complete(coro)


def _walk(  # type: ignore[no-untyped-def]
    api_client,
    database,
    blob_store,
    workspace_id,
    *,
    rate: float | None = None,
    refuse_a1: bool = False,
):
    """The WF-699 state, then WF-701. `rate` sets the prod trace sampling rate first (R6);
    `refuse_a1` makes the platform's answer to the uat deploy a 422 (R8)."""
    from app.platform import settings as settings_service
    from app.worker.dislocation_handlers import register_dislocation_handlers
    from app.worker.rate_table_handlers import register_rate_table_handlers
    from app.worker.rating_handlers import register_rating_handlers
    from app.worker.tasks import execute_job

    record = _run(_world(database, blob_store, workspace_id))
    register_rating_handlers()
    register_dislocation_handlers()
    register_rate_table_handlers()
    api_client.base_url = "http://testserver/api/v1"

    def run_job(job_id: str) -> None:
        _run(execute_job(database, UUID(job_id), blob_store))

    wf699.run_wf699_journey(api_client, record, log=lambda _line: None, run_job=run_job)
    if rate is not None:

        async def set_rate() -> None:
            async with database.unit_of_work() as session:
                await settings_service.set_workspace_setting(
                    session, workspace_id, "rating.trace_sample_rate", rate
                )

        _run(set_rate())
    if refuse_a1:
        import httpx

        real_request = api_client.request

        def request(method: str, url: str, **kwargs: Any) -> httpx.Response:
            if method == "POST" and str(url).endswith("/environments/uat/deployments"):
                return httpx.Response(422, json={"code": "VALIDATION_FAILED", "detail": "A1"})
            return real_request(method, url, **kwargs)

        api_client.request = request
    lines: list[str] = []
    result = wf701.run_wf701_journey(api_client, record, log=lines.append, run_job=run_job)
    return record, result, lines


def _who(record: dict[str, str], name: str) -> dict[str, str]:
    return {"x-dev-principal-id": record[f"{name}_id"], "Workspace-Id": record["workspace_id"]}


@pytest.mark.req("FR-250")
@pytest.mark.req("FR-258")
@pytest.mark.req("FR-259")
@pytest.mark.req("FR-262")
@pytest.mark.req("FR-267")
@pytest.mark.req("FR-268")
@pytest.mark.req("FR-272")
@pytest.mark.req("FR-354")
@pytest.mark.req("FR-429")
@pytest.mark.req("NFR-494")
def test_wf701_journey_runs_end_to_end(api_client, database, blob_store, workspace_id) -> None:  # type: ignore[no-untyped-def]
    """PL 8014 T2 to T4: every in-scope step but A2 and C4 in order (the refusals by problem
    `code`), each effect then read back by this test through a route the journey did not use to
    cause it. NFR-494 is carried by the functional bound only; the verdict is Slice 5's."""
    record, result, lines = _walk(api_client, database, blob_store, workspace_id)

    # T4: the first output line says both facts (RL for DP-1 (a)).
    assert lines[0] == FIRST_LINE
    # T1: the two ruled lines, each printed exactly once in process, and nothing else is a skip.
    assert lines.count(COMPOSE_ONLY_LINE) == 1
    assert lines.count(ERRORS_LINE) == 1
    assert not [line for line in lines if "KNOWN GAP" in line or line.startswith("SKIPPED")]

    # T3/T4: every step, once, in order, each `ok` (A2/C4 are T5's).
    recorded = [step for step in result.step_status if step not in {"A2", "C4"}]
    assert recorded == STEPS_BEFORE_T5
    assert {result.step_status[s] for s in recorded} == {"ok"}

    # T2: the refusals, by the problem `code` the platform returned (probed on `main` 4420f91f).
    # The plan names `DEPLOY_REQUIRES_APPROVAL` for C3 (i) as well, but an unapproved version is
    # refused first, by `_approved_compiled_version`, with 409 `VALIDATION_FAILED`.
    assert result.refusals == {
        "C2": "PROMOTION_ORDER_VIOLATION",
        "C3i": "VALIDATION_FAILED",
        "C3ii": "DEPLOY_REQUIRES_APPROVAL",
    }
    # The journey matched them inside; this test re-checks the server's state: prod's newest
    # deployment is K1 after C1, and uat's is K1 after A1.
    client = api_client
    prod = client.get("/environments/prod/deployments", headers=_who(record, "analyst"))
    assert prod.status_code == 200
    newest = prod.json()["items"][0]
    assert newest["rating_version_ref"] == result.k1_ref
    uat = client.get("/environments/uat/deployments", headers=_who(record, "analyst"))
    assert uat.json()["items"][0]["rating_version_ref"] == result.k1_ref
    assert uat.json()["items"][0]["bundle_hash"] == newest["bundle_hash"]

    # A3 / C1: one `deployment.created` per environment for K1, with the deployer as actor.
    audit = client.get(
        "/audit",
        params={"action": "deployment.created", "limit": 100},
        headers=_who(record, "admin"),
    )
    assert audit.status_code == 200
    for_k1 = [e for e in audit.json()["items"] if result.k1_ref in str(e["after"])]
    assert len(for_k1) == 2  # uat and prod
    assert all(e["after"]["bundle_hash"] == newest["bundle_hash"] for e in for_k1)

    # C7 (i), (ii): the traces for K1 on prod, counted by this test, inside the band [3, 45]
    # and all on K1's hash. N = 2,000 quoted quotes at p = 0.01 (PL 8014 P8).
    traces = client.get(
        "/traces",
        params={"rating_version": result.k1_ref, "limit": 200},
        headers=_who(record, "analyst"),
    ).json()
    quoted = [t for t in traces["items"] if t["sample_reason"] == "rate"]
    assert 3 <= len(quoted) <= 45
    assert result.trace_count == len(quoted)
    assert {t["bundle_hash"] for t in traces["items"]} == {newest["bundle_hash"]}

    # C7 (iii): K2 declines M = 20 quotes; the 100 % floor persists exactly M declined traces.
    declined = client.get(
        "/traces",
        params={"rating_version": result.k2_ref, "limit": 200},
        headers=_who(record, "analyst"),
    ).json()["items"]
    assert len([t for t in declined if t["sample_reason"] == "decline"]) == 20

    # C7 (iv): the refused quote is not traced, on any version.
    every = client.get("/traces", params={"limit": 200}, headers=_who(record, "analyst"))
    assert result.refused_quote_id not in {t["quote_id"] for t in every.json()["items"]}

    # NFR-494's functional bound, labelled as such (not the verdict).
    assert any("functional bound, not the NFR verdict" in line for line in lines)


@pytest.mark.req("FR-259")
def test_wf701_c7_fails_naming_the_band_when_the_sample_rate_is_zero(  # type: ignore[no-untyped-def]
    api_client, database, blob_store, workspace_id
) -> None:
    """R6: at `rating.trace_sample_rate` 0.0 no quoted trace persists; the count 0 is outside
    [3, 45], so C7 (i) fails, naming the band. The band is therefore not vacuous (PL 8014 P8)."""
    with pytest.raises(wf699.JourneyStepFailed) as failure:
        _walk(api_client, database, blob_store, workspace_id, rate=0.0)
    assert failure.value.step == "C7i"
    assert failure.value.code == "TRACE_COUNT_OUTSIDE_BAND"
    assert "[3, 45]" in failure.value.detail


@pytest.mark.req("FR-267")
def test_wf701_a_refused_a1_fails_the_journey_at_a1(  # type: ignore[no-untyped-def]
    api_client, database, blob_store, workspace_id
) -> None:
    """R8's in-process half: with the uat deploy refused, the journey raises at step `A1` with the
    problem's code; `scripts/demo.py` turns that into a line starting `A1:`
    (`test_demo_command.py`)."""
    with pytest.raises(wf699.JourneyStepFailed) as failure:
        _walk(api_client, database, blob_store, workspace_id, refuse_a1=True)
    assert failure.value.step == "A1"
    assert failure.value.code == "VALIDATION_FAILED"
    assert str(failure.value).startswith("A1: VALIDATION_FAILED")
