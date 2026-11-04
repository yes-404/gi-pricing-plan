"""`POST /custom-objectives/preview` over HTTP (FR-1840, `RL-1616` DP-S5-1): who may call it,
the flag, the bounds, and that it leaves nothing behind. The pure core is
`test_objective_preview.py`; this file needs the database."""

from __future__ import annotations

from typing import Any

import pytest
from backend.tests.test_custom_objectives import _principal_holding
from backend.tests.test_custom_objectives_expression import (
    _EXAMPLE_PARAMETERS,
    _LOSS,
    _set_flag,
)
from sqlalchemy import text

from app.db.session import Database
from app.platform import objective_preview as preview_service
from model_schema import PREVIEW_MAX_GRID_POINTS

URL = "/api/v1/custom-objectives/preview"
GRID = {"y": 100.0, "w": 1.0, "f_range": [3.0, 6.0], "n_points": 40}


def _body(**over: Any) -> dict[str, Any]:
    return {"loss": _LOSS, "parameters": _EXAMPLE_PARAMETERS} | over


@pytest.fixture
async def author(database: Database, workspace_id: Any) -> dict[str, str]:
    return await _principal_holding(
        database, workspace_id, {"custom_objective:author", "model:fit", "model:read"}
    )


@pytest.fixture
async def fitter(database: Database, workspace_id: Any) -> dict[str, str]:
    """`model:fit` without `custom_objective:author`."""
    return await _principal_holding(database, workspace_id, {"model:fit", "model:read"})


@pytest.fixture
async def author_without_fit(database: Database, workspace_id: Any) -> dict[str, str]:
    """`custom_objective:author` without `model:fit`."""
    return await _principal_holding(
        database, workspace_id, {"custom_objective:author", "model:read"}
    )


async def _counts(database: Database) -> tuple[int, int, int]:
    async with database.session() as session:
        counts = [
            (await session.execute(text(f"SELECT count(*) FROM {table}"))).scalar_one()
            for table in ("custom_objectives", "objective_certificates", "audit_events")
        ]
    return counts[0], counts[1], counts[2]


@pytest.mark.req("FR-1840")
async def test_with_the_flag_on_a_parse_only_call_answers_ok(
    api_client: Any, author: Any, database: Database, workspace_id: Any
) -> None:
    await _set_flag(database, workspace_id, True)
    response = api_client.post(URL, json=_body(), headers=author)
    assert response.status_code == 200, response.text
    assert response.json()["ok"] is True
    assert response.json()["curve"] is None


@pytest.mark.req("FR-1840")
async def test_a_loss_that_does_not_parse_answers_200_ok_false_with_a_position(
    api_client: Any, author: Any, database: Database, workspace_id: Any
) -> None:
    """WF-702 B1.5: `numpy.where(...)`. A 422 here would be an error on every keystroke."""
    await _set_flag(database, workspace_id, True)
    response = api_client.post(URL, json=_body(loss="numpy.where(f < y, 1, 2)"), headers=author)
    assert response.status_code == 200, response.text
    answer = response.json()
    assert answer["ok"] is False
    assert answer["error"]["reason"] == "grammar"
    assert answer["error"]["line"] == 1
    assert answer["error"]["column"] is not None


@pytest.mark.req("FR-1840")
async def test_a_malformed_request_answers_422(
    api_client: Any, author: Any, database: Database, workspace_id: Any
) -> None:
    await _set_flag(database, workspace_id, True)
    response = api_client.post(URL, json={"parameters": []}, headers=author)
    assert response.status_code == 422, response.text


@pytest.mark.req("FR-1840")
async def test_with_a_grid_the_curve_comes_back(
    api_client: Any, author: Any, database: Database, workspace_id: Any
) -> None:
    await _set_flag(database, workspace_id, True)
    response = api_client.post(URL, json=_body(grid=GRID), headers=author)
    assert response.status_code == 200, response.text
    curve = response.json()["curve"]
    assert len(curve["f"]) == len(curve["loss"]) == len(curve["gradient"]) == 40


def _derive_must_not_run(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(*_: object, **__: object) -> object:
        raise AssertionError("SymPy was reached for an over-bound request")

    monkeypatch.setattr(preview_service, "derive", fail)


_OVER_NODES = " + ".join(["f"] * 150)  # 299 nodes, over FR-145's 200
_OVER_DEPTH = "-" * 25 + "f"  # depth 26, over FR-145's 20


@pytest.mark.req("FR-1840")
@pytest.mark.parametrize(
    "body",
    [
        _body(grid=GRID | {"n_points": PREVIEW_MAX_GRID_POINTS + 1}),
        _body(loss=_OVER_NODES, grid=GRID),
        _body(loss=_OVER_DEPTH, grid=GRID),
        _body(loss=_OVER_NODES),
        _body(loss=_OVER_DEPTH),
    ],
    ids=[
        "grid_points",
        "nodes_with_grid",
        "depth_with_grid",
        "nodes_parse_only",
        "depth_parse_only",
    ],
)
async def test_3a_a_request_over_an_fr145_bound_is_422_validation_failed_before_any_sympy_work(
    api_client: Any,
    author: Any,
    database: Database,
    workspace_id: Any,
    monkeypatch: pytest.MonkeyPatch,
    body: dict[str, Any],
) -> None:
    """Over a bound is 422, never 200 `ok: false`: a loss that does not PARSE is the 200 case
    (`test_a_loss_that_does_not_parse_answers_200_ok_false_with_a_position`)."""
    await _set_flag(database, workspace_id, True)
    _derive_must_not_run(monkeypatch)
    response = api_client.post(URL, json=body, headers=author)
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "VALIDATION_FAILED"


@pytest.mark.req("FR-1840")
async def test_3b_a_timeout_answers_ok_false_not_a_500(
    api_client: Any,
    author: Any,
    database: Database,
    workspace_id: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import threading

    await _set_flag(database, workspace_id, True)
    release = threading.Event()
    monkeypatch.setattr(preview_service, "PREVIEW_TIMEOUT_SECONDS", 0.2)
    monkeypatch.setattr(preview_service, "derive", lambda *a, **k: release.wait(5))
    try:
        response = api_client.post(URL, json=_body(grid=GRID), headers=author)
    finally:
        release.set()
    assert response.status_code == 200, response.text
    assert response.json()["error"]["reason"] == "timeout"
    assert preview_service.wait_idle(timeout=5)


@pytest.mark.req("FR-367")
async def test_without_the_author_permission_the_answer_is_403_whatever_the_flag(
    api_client: Any, fitter: Any, database: Database, workspace_id: Any
) -> None:
    for flag in (False, True):
        await _set_flag(database, workspace_id, flag)
        response = api_client.post(URL, json=_body(), headers=fitter)
        assert response.status_code == 403, response.text


@pytest.mark.req("FR-367")
async def test_without_model_fit_the_answer_is_403_though_the_author_permission_is_held(
    api_client: Any, author_without_fit: Any, database: Database, workspace_id: Any
) -> None:
    for flag in (False, True):
        await _set_flag(database, workspace_id, flag)
        response = api_client.post(URL, json=_body(), headers=author_without_fit)
        assert response.status_code == 403, response.text


@pytest.mark.req("FR-150")
async def test_with_both_permissions_and_the_flag_off_the_answer_is_409(
    api_client: Any, author: Any, database: Database, workspace_id: Any
) -> None:
    response = api_client.post(URL, json=_body(grid=GRID), headers=author)
    assert response.status_code == 409, response.text
    assert response.json()["code"] == "OBJECTIVE_KIND_NOT_ENABLED"


@pytest.mark.req("FR-1840")
async def test_a_successful_preview_writes_no_row_and_no_audit_event(
    api_client: Any, author: Any, database: Database, workspace_id: Any
) -> None:
    await _set_flag(database, workspace_id, True)
    before = await _counts(database)
    for body in (_body(), _body(grid=GRID), _body(loss="numpy.where(f < y, 1, 2)")):
        assert api_client.post(URL, json=body, headers=author).status_code == 200
    assert await _counts(database) == before
