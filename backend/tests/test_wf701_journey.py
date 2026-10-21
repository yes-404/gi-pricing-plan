"""WF-701 — the deployment steps A1-A6, C1-C4, C6 and C7, walked over HTTP (PL-1710, SL-1711).

`docs/workflows/WF-00701-deploy-and-monitor.md` is the journey this file proves:
`examples/fremtpl2/journey_wf701.py` is an `httpx` client of `/api/v1` that walks the deployment
steps on the state WF-699's journey leaves, and these tests run that module against the app in
process. The monitoring steps (C5, D1-D4) and A3's notification are P4's (the maintainer's entry
"2026-10-14 09:50:37 BST").

The in-process run has one process and no replicas, so A2 (iii), C4 (iii) and C6's replica limb
are printed as the one ruled line `COMPOSE-ONLY A2/C4/C6 replica limb` and never as `ok`; the
compose run (`scripts/demo.py --journey wf-701 --target compose`) walks them.

Marker form: `scripts/req-coverage.py` reads only the decorator form of the `req` marker with an
FR or NFR id, and a workflow id is not one, so (as `test_wf699_journey.py` does for `WF-699`) the
requirement ids the journey exercises are the markers and `WF-701` is named here and in the test
names.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

_EXAMPLE = Path(__file__).resolve().parents[2] / "examples" / "fremtpl2"
sys.path.insert(0, str(_EXAMPLE))
import journey_wf701 as j  # noqa: E402


@pytest.mark.req("FR-259")
def test_wf701_the_ruled_lines_are_exactly_the_two() -> None:
    """The only lines admitted by ruling: the replica limb (one process cannot walk it) and the
    errors limb RL-1712 rules walked, never a `KNOWN GAP C7-errors`."""
    assert j.RULED_LINES == (
        "COMPOSE-ONLY A2/C4/C6 replica limb",
        "C7-errors: refused, not traced (FR-259, RL-1712)",
    )
    assert not [line for line in j.RULED_LINES if "KNOWN GAP" in line]


@pytest.mark.req("FR-259")
def test_an_unruled_skip_fails_the_journey() -> None:
    """The form of `test_wf699_journey.py`'s unowned-skip test: a skip line that is not one of the
    two ruled lines fails, so a step cannot be quietly dropped."""
    ruled = list(j.RULED_LINES)
    j.check_lines(ruled, replica_limb=False)
    for line in ("SKIPPED A5: later", "KNOWN GAP C7-errors: FD-1706", "COMPOSE-ONLY C6 only"):
        with pytest.raises(j.JourneyStepFailed) as failure:
            j.check_lines([*ruled, line], replica_limb=False)
        assert failure.value.code == "UNRULED_SKIP"


@pytest.mark.req("FR-259")
def test_each_ruled_line_is_printed_the_right_number_of_times() -> None:
    both = list(j.RULED_LINES)
    with pytest.raises(j.JourneyStepFailed) as missing:
        j.check_lines([j.C7_ERRORS], replica_limb=False)  # the replica limb was not walked
    assert missing.value.code == "RULED_LINE_COUNT"
    with pytest.raises(j.JourneyStepFailed) as twice:
        j.check_lines([*both, j.C7_ERRORS], replica_limb=False)
    assert twice.value.code == "RULED_LINE_COUNT"
    with pytest.raises(j.JourneyStepFailed):
        j.check_lines(both, replica_limb=True)  # walked on compose: the ruled line must be absent
    j.check_lines([j.C7_ERRORS], replica_limb=True)


@pytest.mark.req("FR-268")
def test_the_step_order_names_every_in_scope_step_once() -> None:
    assert len(set(j.STEP_ORDER)) == len(j.STEP_ORDER)
    steps = {step.split("(")[0] for step in j.STEP_ORDER}
    assert {"A1", "A2", "A3", "A4", "A5", "A6", "C1", "C2", "C3", "C4", "C6", "C7"} <= steps
    # C5 and D1-D4 are P4's: not walked here.
    assert not {"C5", "D1", "D2", "D3", "D4"} & steps


@pytest.mark.req("FR-259")
def test_the_c7_band_is_pre_registered_and_not_vacuous() -> None:
    """P8: Binomial(2000, 0.01), band [3, 45], outside it with probability 8.030e-07 (exact
    arithmetic). At p = 0 the count is 0, outside the band, so the band can fail (R6)."""
    outside = j.outside_band_probability(2000, Fraction(1, 100), (3, 45))
    assert abs(float(outside) - 8.030e-07) < 5e-10
    with pytest.raises(j.JourneyStepFailed) as failure:
        j.check_trace_count(0)
    assert failure.value.step == "C7"
    assert "OUTSIDE_BAND_3_45" in str(failure.value.code)
    j.check_trace_count(20)
    j.check_trace_count(3)
    j.check_trace_count(45)
    with pytest.raises(j.JourneyStepFailed):
        j.check_trace_count(46)


@pytest.mark.req("FR-268")
def test_a_response_with_a_third_hash_fails_the_old_or_new_assertion() -> None:
    """R4: the proof PL-1237 Task 5 asks of S5, repeated on the journey (an injected response)."""
    old, new, third = "sha256:" + "a" * 64, "sha256:" + "b" * 64, "sha256:" + "c" * 64
    j.check_old_or_new("A2", [old, new, old], old, new)
    with pytest.raises(j.JourneyStepFailed) as failure:
        j.check_old_or_new("A2", [old, third, new], old, new)
    assert failure.value.code == "BUNDLE_HASH_NEITHER_OLD_NOR_NEW"
    j.check_none_old("A2", [new, new], old)
    with pytest.raises(j.JourneyStepFailed) as stale:
        j.check_none_old("C4", [new, old], old)
    assert stale.value.code == "OLD_BUNDLE_SERVED_AFTER_THE_DEPLOY"


@pytest.mark.req("FR-268")
def test_a_commit_set_short_of_the_replicas_fails_naming_the_missing_one() -> None:
    """R5: the audit log's COMMIT set against the replicas the stack reports."""
    processes = {
        "host-a:11:100": "committed",
        "host-b:12:101": "possibly_stale",
        "host-c:13:102": "pruned_stale",
    }
    with pytest.raises(j.JourneyStepFailed) as failure:
        j.check_commit_set("A2", processes, frozenset({"host-a", "host-b"}))
    assert failure.value.code == "COMMIT_SET_DIFFERS_FROM_THE_REPLICAS"
    assert "missing host-b" in failure.value.detail
    j.check_commit_set(
        "A2",
        {"host-a:1:1": "committed", "host-b:2:2": "committed"},
        frozenset({"host-a", "host-b"}),
    )


@pytest.mark.req("FR-258")
def test_the_minimum_premium_is_read_from_the_constraints_rung() -> None:
    applied = {
        "premium_ladder": [
            {"rung": "constraints", "operation": {"applied": ["MIN_PREMIUM_APPLIED"]}}
        ]
    }
    none = {"premium_ladder": [{"rung": "constraints", "operation": {"applied": []}}]}
    assert j.binds_min_premium(applied)
    assert not j.binds_min_premium(none)
    assert not j.binds_min_premium({"premium_ladder": [{"rung": "payable_premium"}]})


def test_the_contract_sample_is_deterministic_and_spread() -> None:
    contract: list[dict[str, Any]] = [
        {"name": "area", "type": "enum", "domain": list("ABCDEF")},
        {"name": "bonus_malus", "type": "int", "min": 50, "max": 150},
        {"name": "current_premium_minor", "type": "int", "min": 0},
    ]
    first = j.contract_sample(contract, {"current_premium_minor": 55000}, 200)
    assert first == j.contract_sample(contract, {"current_premium_minor": 55000}, 200)
    assert len({json.dumps(row, sort_keys=True) for row in first}) > 100
    assert {row["area"] for row in first} == set("ABCDEF")
    assert all(50 <= row["bonus_malus"] <= 150 for row in first)
    assert {row["current_premium_minor"] for row in first} == {55000}


@pytest.mark.req("FR-250")
def test_k1_is_the_minimum_premium_of_the_shipped_change() -> None:
    """K1 adds a clamp to 180 with the reason code the shipped v2 algorithm's `s_floor` carries:
    it is the `min_premium 150 -> 180` change of `fremtpl2-rate.changes.json`, not a new figure.
    (The live algorithm has no floor, so the clamp is added after `s_premium`, not replaced.)"""
    rating = _EXAMPLE / "rating"
    k1: dict[str, Any] = json.loads(j.K1_FILE.read_text(encoding="utf-8"))
    v2 = json.loads((rating / "fremtpl2-rate.rating-algorithm.v2.json").read_text(encoding="utf-8"))
    shipped = next(s for s in v2["steps"] if s["step_id"] == "s_floor")
    step = k1["add_step"]
    assert step["clamp_bounds"] == shipped["clamp_bounds"]
    assert step["reason_code"] == shipped["reason_code"]
    assert step["on_violation"] == "clamp"
    assert k1["after"] == "s_premium"


@pytest.mark.req("FR-259")
def test_k2_adds_one_declining_constraint_with_a_reason_code() -> None:
    k2: dict[str, Any] = json.loads(j.K2_FILE.read_text(encoding="utf-8"))
    step = k2["add_step"]
    assert step["type"] == "constraint"
    assert step["on_violation"] == "decline"
    assert step["reason_code"]
    assert "bonus_malus" in step["condition"]
    low, high = k2["declined_bonus_malus"]
    assert 140 < low <= high <= 150  # above the limit, inside the contract's 50..150


def _run_in_process(
    api_client: Any,
    database: Any,
    blob_store: Any,
    workspace_id: Any,
    *,
    before_step: Any = None,
) -> tuple[Any, list[str]]:
    """WF-699's journey, then WF-701's, over the app in process: the harness of
    `test_wf699_journey.test_wf699_journey_runs_end_to_end`, `run_job` running each Job."""
    import asyncio
    from uuid import UUID

    from backend.tests.test_wf699_journey import _world

    from app.worker.dislocation_handlers import register_dislocation_handlers
    from app.worker.rate_table_handlers import register_rate_table_handlers
    from app.worker.rating_handlers import register_rating_handlers
    from app.worker.tasks import execute_job

    loop = asyncio.get_event_loop()
    record = loop.run_until_complete(_world(database, blob_store, workspace_id))
    register_rating_handlers()
    register_dislocation_handlers()
    register_rate_table_handlers()
    api_client.base_url = "http://testserver/api/v1"
    lines: list[str] = []

    def run_job(job_id: str) -> None:
        loop.run_until_complete(execute_job(database, UUID(job_id), blob_store))

    def hook(step: str) -> None:
        if before_step is not None:
            before_step(step, record)

    try:
        result = j.run_wf701_journey(
            api_client, record, log=lines.append, run_job=run_job, before_step=hook
        )
    except j.JourneyStepFailed as failure:
        pytest.fail(f"{failure} :: {failure.detail} :: after {lines[-1:]}")
    return result, lines


@pytest.mark.req("FR-238")
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
    """Every in-scope step of WF-701, in order, each by its status and a read-back effect: the
    refusals by their problem `code` (C2 `EVIDENCE_INCOMPLETE` and `PROMOTION_ORDER_VIOLATION`,
    C3 `DEPLOY_REQUIRES_APPROVAL`, the FR-238 extra `VALIDATION_FAILED`), K1 and K2 through
    two approvers, the stream across each switch, C7's band and its exact declined count.

    **One process, no replicas:** the replica limb is the one ruled `COMPOSE-ONLY` line."""
    result, lines = _run_in_process(api_client, database, blob_store, workspace_id)

    assert list(result.step_status) == list(j.STEP_ORDER)
    assert set(result.step_status.values()) == {"ok"}
    assert lines.count(j.FIRST_LINE) == 1
    assert lines.index(j.FIRST_LINE) < lines.index(j.C7_ERRORS)
    assert lines.count(j.COMPOSE_ONLY) == 1
    assert lines.count(j.C7_ERRORS) == 1
    assert not [line for line in lines if "KNOWN GAP C7-errors" in line]
    assert any(line.startswith("PRECONDITION dev:") for line in lines)
    assert result.k1_bundle_hash.startswith("sha256:")
    assert result.k2_bundle_hash != result.k1_bundle_hash
    assert result.c4_elapsed_s < j.FUNCTIONAL_BOUND_S
    assert j.C7_BAND[0] <= result.c7_count <= j.C7_BAND[1]
    assert result.c7_declined == j.C7_DECLINES
    assert result.a5_totals["changed"] > 0


@pytest.mark.req("FR-259")
def test_c7_fails_naming_the_band_when_the_sample_rate_is_zero(  # type: ignore[no-untyped-def]
    api_client, database, blob_store, workspace_id
) -> None:
    """R6: with prod's `rating.trace_sample_rate` set to 0.0 through the settings API, the C7 (i)
    count is 0, outside [3, 45], and the step fails naming the band."""

    def break_the_rate(step: str, record: dict[str, str]) -> None:
        if step != "C7(i)":
            return
        response = api_client.put(
            "/environments/prod/settings",
            json={"values": {"rating.trace_sample_rate": 0.0}},
            headers={
                "x-dev-principal-id": record["admin_id"],
                "Workspace-Id": record["workspace_id"],
            },
        )
        assert response.status_code == 200, response.text

    with pytest.raises(pytest.fail.Exception) as failure:
        _run_in_process(api_client, database, blob_store, workspace_id, before_step=break_the_rate)
    assert "C7: TRACE_COUNT_0_OUTSIDE_BAND_3_45" in str(failure.value)
