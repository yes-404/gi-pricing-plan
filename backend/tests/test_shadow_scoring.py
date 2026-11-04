"""Shadow scoring after the response (`03` §4.13, FR-271; WK-674 Slice 6, `RL-1834` D2 items 4
to 6).

The caller is `test_score.py`'s `uat` Service Account and its `refs_scored` fixture records the
ref of each bundle resolution, so the live ref is first and the candidate's second. Starlette's
test client runs a response's background task before it returns, so a row the task writes is
visible to the assert that follows the request. The shadow flag is an Environment setting and
Environments are deployment-wide, so every test that turns it on turns it off again.
"""

# Fixtures are imported from the sibling modules that define them, as the other test files do,
# so a test parameter redefines the imported name (F811).
# ruff: noqa: F811

from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from typing import Any
from uuid import UUID

import pytest
from backend.tests.test_score import (  # noqa: F401
    _LIVE_APPS,
    SCORE_URL,
    _quote,
    _run,
    _scored,
    admin_headers,
    client,
    plant_deployment,
    refs_scored,
    scoring_headers,
)
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.api import score as score_module
from app.db.models import EnvironmentRow, ShadowConfigRow, ShadowResultRow
from app.platform import settings as settings_service
from model_schema import new_uuid7

_FLAG = "features.shadow_scoring_enabled"
LIVE = "rating_version:live-rv@3"
CANDIDATE = "rating_version:candidate-rv@1"


async def _set_flag(database: Any, value: bool) -> None:
    async with database.unit_of_work() as session:
        await settings_service.set_environment_setting(session, "uat", _FLAG, value, None)


@pytest.fixture
def shadow_flag(database: Any) -> Iterator[Callable[[bool], None]]:
    """Set `uat`'s shadow flag; it is switched off again when the test ends."""
    try:
        yield lambda value: _run(_set_flag(database, value))
    finally:
        _run(_set_flag(database, False))


async def _configure(database: Any, workspace_id: UUID, fraction: float) -> None:
    """A `shadow_configs` row inserted directly: the write route is `test_shadow_write.py`'s."""
    async with database.unit_of_work() as session:
        env_id = (
            await session.execute(select(EnvironmentRow.id).where(EnvironmentRow.slug == "uat"))
        ).scalar_one()
        session.add(
            ShadowConfigRow(
                id=new_uuid7(),
                workspace_id=workspace_id,
                environment_id=env_id,
                candidate_rating_version_ref=CANDIDATE,
                candidate_bundle_hash="sha256:" + "b" * 64,
                fraction=fraction,
                written_by=new_uuid7(),
            )
        )


async def _results(database: Any, workspace_id: UUID) -> list[ShadowResultRow]:
    async with database.session() as session:
        return list(
            (
                await session.execute(
                    select(ShadowResultRow).where(ShadowResultRow.workspace_id == workspace_id)
                )
            ).scalars()
        )


def _live_quote(client: TestClient, headers: dict[str, str], ref: str | None = None):
    return client.post(SCORE_URL, json=_quote({"rating_version_ref": ref}), headers=headers)


def _live(database: Any, workspace_id: UUID) -> UUID:
    return _run(plant_deployment(database, workspace_id, "uat", LIVE))


@pytest.mark.req("FR-271")
def test_a_sampled_quote_is_also_scored_by_the_candidate_and_both_results_are_recorded(
    client, scoring_headers, refs_scored, database, workspace_id, shadow_flag
) -> None:
    """Both `ScoringResult`s are stored without `trace` and `timing_ms`; the candidate's is
    recorded and never returned, so the caller's body is the live result alone."""
    live_id = _live(database, workspace_id)
    _run(_configure(database, workspace_id, 1.0))
    shadow_flag(True)
    response = _live_quote(client, scoring_headers)
    assert response.status_code == 200, response.text
    assert response.json()["rating_version_ref"] == LIVE
    assert CANDIDATE not in response.text
    assert [str(r) for r in refs_scored] == [LIVE, CANDIDATE]
    (row,) = _run(_results(database, workspace_id))
    assert row.live_deployment_id == live_id
    assert row.live_result["rating_version_ref"] == LIVE
    assert row.candidate_result["rating_version_ref"] == CANDIDATE
    for stored in (row.live_result, row.candidate_result):
        assert "trace" not in stored
        assert "timing_ms" not in stored
        assert stored["outputs"] == {"payable_premium_minor": 12_000}


@pytest.mark.req("FR-271", "NFR-499")
def test_a_shadow_result_holds_no_quote_input(
    client, scoring_headers, refs_scored, database, workspace_id, shadow_flag
) -> None:
    """The row is not a quote-input store: nothing the caller sent is in it."""
    _live(database, workspace_id)
    _run(_configure(database, workspace_id, 1.0))
    shadow_flag(True)
    body = {**_quote({"rating_version_ref": None}), "inputs": {"premium_in": 987_654_321}}
    assert client.post(SCORE_URL, json=body, headers=scoring_headers).status_code == 200
    (row,) = _run(_results(database, workspace_id))
    assert "987654321" not in json.dumps([row.live_result, row.candidate_result])


@pytest.mark.req("FR-271", "FR-449")
def test_with_the_flag_off_nothing_is_attached_and_no_row_is_written(
    client, scoring_headers, refs_scored, database, workspace_id, monkeypatch
) -> None:
    """A configuration exists, the flag is off: the candidate is never resolved or scored and
    `shadow_results` gains no row."""
    _live(database, workspace_id)
    _run(_configure(database, workspace_id, 1.0))
    response = _live_quote(client, scoring_headers)
    assert response.status_code == 200, response.text
    assert [str(r) for r in refs_scored] == [LIVE]
    assert _run(_results(database, workspace_id)) == []


@pytest.mark.req("FR-271")
def test_with_no_configuration_nothing_is_scored(
    client, scoring_headers, refs_scored, database, workspace_id, shadow_flag
) -> None:
    _live(database, workspace_id)
    shadow_flag(True)
    assert _live_quote(client, scoring_headers).status_code == 200
    assert [str(r) for r in refs_scored] == [LIVE]
    assert _run(_results(database, workspace_id)) == []


@pytest.mark.req("FR-271")
def test_a_draw_at_or_above_the_fraction_is_not_shadow_scored(
    client, scoring_headers, refs_scored, database, workspace_id, shadow_flag, monkeypatch
) -> None:
    _live(database, workspace_id)
    _run(_configure(database, workspace_id, 0.5))
    shadow_flag(True)
    monkeypatch.setattr(score_module.random, "random", lambda: 0.5)
    assert _live_quote(client, scoring_headers).status_code == 200
    assert [str(r) for r in refs_scored] == [LIVE]
    assert _run(_results(database, workspace_id)) == []


@pytest.mark.req("FR-271")
def test_a_quote_naming_a_rating_version_is_not_shadow_scored(
    client, scoring_headers, refs_scored, database, workspace_id, shadow_flag
) -> None:
    """Shadow scoring covers default-live quotes only; a what-if quote is nobody's live price."""
    _live(database, workspace_id)
    _run(_configure(database, workspace_id, 1.0))
    shadow_flag(True)
    assert _live_quote(client, scoring_headers, LIVE).status_code == 200
    assert _run(_results(database, workspace_id)) == []


@pytest.mark.req("FR-271")
def test_a_failure_of_the_candidate_never_reaches_the_caller(
    client, scoring_headers, refs_scored, database, workspace_id, shadow_flag, monkeypatch
) -> None:
    """The candidate's scoring raises: the response is the live quote, 200, and no row is
    written. Deliberately broken input: the second `score_one` call raises."""
    _live(database, workspace_id)
    _run(_configure(database, workspace_id, 1.0))
    shadow_flag(True)
    calls: list[int] = []

    async def flaky(*_a: Any, **_k: Any) -> Any:
        calls.append(1)
        if len(calls) > 1:
            raise RuntimeError("candidate bundle exploded")
        return _scored(rating_version_ref=refs_scored[-1])

    monkeypatch.setattr(score_module, "score_one", flaky)
    response = _live_quote(client, scoring_headers)
    assert response.status_code == 200, response.text
    assert len(calls) == 2
    assert _run(_results(database, workspace_id)) == []


@pytest.mark.req("FR-271")
def test_the_response_is_the_same_with_and_without_shadow_scoring(
    client, scoring_headers, refs_scored, database, workspace_id, shadow_flag
) -> None:
    _live(database, workspace_id)
    _run(_configure(database, workspace_id, 1.0))
    off = _live_quote(client, scoring_headers)
    shadow_flag(True)
    on = _live_quote(client, scoring_headers)
    assert off.status_code == on.status_code == 200
    assert off.json() == on.json()
    count = _run(_count(database, workspace_id))
    assert count == 1


async def _count(database: Any, workspace_id: UUID) -> int:
    async with database.session() as session:
        return (
            await session.execute(
                select(func.count())
                .select_from(ShadowResultRow)
                .where(ShadowResultRow.workspace_id == workspace_id)
            )
        ).scalar_one()
