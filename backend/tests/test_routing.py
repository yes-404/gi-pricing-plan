"""Date-routing selection in `POST /api/v1/score` (`03` §4.13, FR-270; WK-674 Slice 6,
`RL-1834` D1 (b) and (c)).

Two things must hold. No Rating Version that was not promoted into the caller's Environment is
ever selected, whatever a stored rule says; and with the Environment's routing flag off, scoring
is the LiveRefs path of today, with the selector never entered.

The caller is `test_score.py`'s `uat` Service Account, and its `refs_scored` fixture records the
ref each request resolved a bundle for, so "B's bundle was never loaded" is an assert on that list.
The routing flag is an Environment setting, and Environments are deployment-wide, so every test
that turns it on turns it off again (`routing_flag`).
"""

# Fixtures are imported from the sibling modules that define them, as the other test files do,
# so a test parameter redefines the imported name (F811).
# ruff: noqa: F811

from __future__ import annotations

import json
import logging
import traceback
from collections.abc import Callable, Iterator
from typing import Any
from uuid import UUID

import pytest
from backend.tests.test_score import (  # noqa: F401
    _LIVE_APPS,
    SCORE_URL,
    _quote,
    _run,
    admin_headers,
    client,
    plant_deployment,
    refs_scored,
    scoring_headers,
)
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.models import EnvironmentRow, RoutingRuleRow
from app.platform import routing
from app.platform import settings as settings_service
from model_schema import new_uuid7

_FLAG = "features.date_routing_enabled"
LIVE = "rating_version:live-rv@3"
EARLIER = "rating_version:earlier-rv@1"
UNPROMOTED = "rating_version:unpromoted-rv@1"


async def _set_flag(database: Any, value: bool) -> None:
    async with database.unit_of_work() as session:
        await settings_service.set_environment_setting(session, "uat", _FLAG, value, None)


@pytest.fixture
def routing_flag(database: Any) -> Iterator[Callable[[bool], None]]:
    """Set `uat`'s routing flag; it is switched off again when the test ends."""
    try:
        yield lambda value: _run(_set_flag(database, value))
    finally:
        _run(_set_flag(database, False))


async def _write_rule(
    database: Any, workspace_id: UUID, ranges: list[dict[str, Any]], environment: str = "uat"
) -> None:
    """A `routing_rules` row inserted directly, bypassing `PUT .../routing`: deliberately
    broken input where a range names what the route would have refused."""
    async with database.unit_of_work() as session:
        env_id = (
            await session.execute(
                select(EnvironmentRow.id).where(EnvironmentRow.slug == environment)
            )
        ).scalar_one()
        session.add(
            RoutingRuleRow(
                id=new_uuid7(),
                workspace_id=workspace_id,
                environment_id=env_id,
                ranges=ranges,
                written_by=new_uuid7(),
            )
        )


def _range(ref: str, deployment_id: UUID, start: str, end: str | None) -> dict[str, Any]:
    return {
        "rating_version_ref": ref,
        "effective_from": start,
        "effective_to": end,
        "deployment_id": str(deployment_id),
    }


def _score(client: TestClient, headers: dict[str, str], date: str = "2026-09-01"):
    body = {**_quote({"rating_version_ref": None}), "effective_date": date}
    return client.post(SCORE_URL, json=body, headers=headers)


def _content(response: Any) -> str:
    """The body without `timing_ms`, the field `pricing_core` itself excludes as non-content
    (`score.py:297`): two calls never agree on it."""
    body = response.json()
    body.pop("timing_ms", None)
    return json.dumps(body, sort_keys=True, separators=(",", ":"))


@pytest.mark.req("FR-270")
def test_a_range_inside_its_dates_selects_its_promoted_version(
    client, scoring_headers, refs_scored, database, workspace_id, routing_flag
) -> None:
    """The flag-on control: the quote inside the range is scored by the range's version, not
    the Environment's live one."""
    earlier_id = _run(plant_deployment(database, workspace_id, "uat", EARLIER))
    _run(plant_deployment(database, workspace_id, "uat", LIVE))
    _run(_write_rule(database, workspace_id, [_range(EARLIER, earlier_id, "2026-01-01", None)]))
    routing_flag(True)
    response = _score(client, scoring_headers)
    assert response.status_code == 200, response.text
    assert [str(r) for r in refs_scored] == [EARLIER]


@pytest.mark.req("FR-270")
def test_a_quote_outside_every_range_is_scored_by_the_live_version(
    client, scoring_headers, refs_scored, database, workspace_id, routing_flag
) -> None:
    earlier_id = _run(plant_deployment(database, workspace_id, "uat", EARLIER))
    _run(plant_deployment(database, workspace_id, "uat", LIVE))
    past = _range(EARLIER, earlier_id, "2025-01-01", "2026-01-01")
    _run(_write_rule(database, workspace_id, [past]))
    routing_flag(True)
    assert _score(client, scoring_headers).status_code == 200
    assert [str(r) for r in refs_scored] == [LIVE]


@pytest.mark.req("FR-270")
def test_the_end_of_a_range_is_exclusive(
    client, scoring_headers, refs_scored, database, workspace_id, routing_flag
) -> None:
    earlier_id = _run(plant_deployment(database, workspace_id, "uat", EARLIER))
    _run(plant_deployment(database, workspace_id, "uat", LIVE))
    ends = _range(EARLIER, earlier_id, "2026-01-01", "2026-09-01")
    _run(_write_rule(database, workspace_id, [ends]))
    routing_flag(True)
    assert _score(client, scoring_headers, "2026-09-01").status_code == 200
    assert [str(r) for r in refs_scored] == [LIVE]


@pytest.mark.req("FR-270")
def test_an_explicit_ref_is_never_routed(
    client, scoring_headers, refs_scored, database, workspace_id, routing_flag
) -> None:
    """Routing applies only to a quote that names no Rating Version."""
    earlier_id = _run(plant_deployment(database, workspace_id, "uat", EARLIER))
    _run(plant_deployment(database, workspace_id, "uat", LIVE))
    _run(_write_rule(database, workspace_id, [_range(EARLIER, earlier_id, "2026-01-01", None)]))
    routing_flag(True)
    body = {**_quote({"rating_version_ref": LIVE}), "effective_date": "2026-09-01"}
    assert client.post(SCORE_URL, json=body, headers=scoring_headers).status_code == 200
    assert [str(r) for r in refs_scored] == [LIVE]


@pytest.mark.req("FR-270")
def test_a_version_promoted_only_to_another_environment_is_never_selected(
    client, scoring_headers, refs_scored, database, workspace_id, routing_flag
) -> None:
    """`RL-1834` D1 (b), at selection. UNPROMOTED is deployed to `dev` only; a rule row for
    `uat` (inserted past the route, which would refuse it) names it, pinned to its `dev`
    Deployment, and covers the quote's date. The quote is scored by the live version and the
    unpromoted version's bundle is never loaded. Red first against a selector without the pin
    check, which would take the range at its word."""
    dev_id = _run(plant_deployment(database, workspace_id, "dev", UNPROMOTED))
    _run(plant_deployment(database, workspace_id, "uat", LIVE))
    _run(_write_rule(database, workspace_id, [_range(UNPROMOTED, dev_id, "2026-01-01", None)]))
    routing_flag(True)
    response = _score(client, scoring_headers)
    assert response.status_code == 200, response.text
    assert response.json()["rating_version_ref"] == LIVE
    assert [str(r) for r in refs_scored] == [LIVE]
    assert UNPROMOTED not in {str(r) for r in refs_scored}


@pytest.mark.req("FR-270")
def test_a_pin_naming_a_deployment_of_a_different_version_is_ignored(
    client, scoring_headers, refs_scored, database, workspace_id, routing_flag
) -> None:
    """The pinned Deployment is in `uat` but is a Deployment of another version than the range
    names: the pair does not hold, so the range is ignored."""
    live_id = _run(plant_deployment(database, workspace_id, "uat", LIVE))
    _run(_write_rule(database, workspace_id, [_range(UNPROMOTED, live_id, "2026-01-01", None)]))
    routing_flag(True)
    assert _score(client, scoring_headers).status_code == 200
    assert [str(r) for r in refs_scored] == [LIVE]


@pytest.mark.req("FR-270", "FR-449")
def test_with_the_flag_off_scoring_is_unchanged_and_the_selector_is_not_entered(
    client,
    scoring_headers,
    refs_scored,
    database,
    workspace_id,
    routing_flag,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`RL-1834` D1 (c). Baseline: quotes inside and outside a would-be range, scored with no
    `routing_rules` row at all. Then a rule that covers the first quote is stored and the same
    quotes are scored again with the flag off: each body, less `timing_ms`, is equal to its
    baseline and the selector records zero calls. The control (flag on) shows the comparison can
    fail: the inside quote then resolves to the rule's version."""
    earlier_id = _run(plant_deployment(database, workspace_id, "uat", EARLIER))
    _run(plant_deployment(database, workspace_id, "uat", LIVE))
    dates = ("2026-09-01", "2025-06-01")
    baseline = [_content(_score(client, scoring_headers, d)) for d in dates]
    assert [str(r) for r in refs_scored] == [LIVE, LIVE]

    calls: list[object] = []
    real = routing.select_range

    async def spy(*args: Any, **kwargs: Any) -> Any:
        calls.append(args)
        return await real(*args, **kwargs)

    monkeypatch.setattr(routing, "select_range", spy)
    _run(_write_rule(database, workspace_id, [_range(EARLIER, earlier_id, "2026-01-01", None)]))
    refs_scored.clear()
    again = [_content(_score(client, scoring_headers, d)) for d in dates]
    assert again == baseline
    assert [str(r) for r in refs_scored] == [LIVE, LIVE]
    assert calls == []

    routing_flag(True)
    refs_scored.clear()
    assert _score(client, scoring_headers, dates[0]).status_code == 200
    assert [str(r) for r in refs_scored] == [EARLIER]
    assert len(calls) == 1


@pytest.mark.req("FR-270")
@pytest.mark.parametrize("failing", ["select_range", "resolve"])
def test_a_routing_selection_failure_fails_the_quote_and_never_falls_back(
    client,
    scoring_headers,
    refs_scored,
    database,
    workspace_id,
    routing_flag,
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
    failing: str,
) -> None:
    """The maintainer's ruling of 2026-10-22 17:34:47 BST item 4 (`03` §4.13, Selection): with
    the flag on, a failure to read the routing flag (`resolve`) or to select a range
    (`select_range`) refuses the quote 500 `INTERNAL_ERROR`. The default-live version is never
    scored in its place, because a fallback could price from the wrong Rating Version, and the
    log names the cause: an ERROR "request failed" record whose sanitised exception text begins
    with the raised class and whose traceback frames include the failing function. The control
    is the same quote with both healthy: it is scored (200)."""
    _run(plant_deployment(database, workspace_id, "uat", LIVE))
    routing_flag(True)
    assert _score(client, scoring_headers).status_code == 200
    assert [str(r) for r in refs_scored] == [LIVE]

    if failing == "select_range":

        async def select_range(*_a: Any, **_k: Any) -> Any:
            raise RuntimeError("routing store down")

        monkeypatch.setattr(routing, "select_range", select_range)
    else:
        real = settings_service.resolve

        async def resolve(session: Any, settings: Any, workspace: Any, key: str, *a: Any) -> Any:
            if key == _FLAG:
                raise RuntimeError("settings store down")
            return await real(session, settings, workspace, key, *a)

        monkeypatch.setattr(settings_service, "resolve", resolve)
    refs_scored.clear()
    with caplog.at_level(logging.ERROR):
        failed = _score(client, scoring_headers)
    assert failed.status_code == 500
    assert failed.json()["code"] == "INTERNAL_ERROR"
    assert refs_scored == []
    (record,) = [r for r in caplog.records if r.getMessage() == "request failed"]
    assert record.levelno == logging.ERROR
    assert record.exc_info is not None
    _cls, value, tb = record.exc_info
    assert str(value).startswith("RuntimeError")
    assert failing in [frame.name for frame in traceback.extract_tb(tb)]
