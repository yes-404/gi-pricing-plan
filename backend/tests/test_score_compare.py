"""`POST /api/v1/score/compare` — the Quote Sandbox compare endpoint (FR-262, `03` §5.1;
WK-672 Slice 4, PL-1213 Tasks 4-5).

One Quote Context is scored against two Rating Versions through two `score_one` calls, and the
two traces are diffed. The caller holds `rating:read` (DP-S4-3); nothing is persisted or logged
(NFR-499). Every test drives the **route** through the HTTP client, never the service function.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import pytest
import pytest_asyncio
from backend.tests.test_rating_version_compile import (
    _empty_pins,
    _insert_version,
    _minimal_algorithm,
    _run_compile_job,
)
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.api import score as score_module
from app.api.deps import DEV_PRINCIPAL_HEADER
from app.config import Settings
from app.db.models import JobRow, ScoringTraceRow
from app.main import create_app
from app.platform import settings as settings_service
from app.worker.rating_handlers import register_rating_handlers
from model_schema import JobStatus
from pricing_core.safe_error import CodedError

COMPARE_URL = "/api/v1/score/compare"
BASE_REF = "rating_version:minimal-rv@1"
CHANGED_REF = "rating_version:minimal-rv@2"


@pytest.fixture
def client(api_settings: Settings) -> Any:
    with TestClient(create_app(api_settings), raise_server_exceptions=False) as c:
        yield c


@pytest_asyncio.fixture
async def reader_headers(workspace_id: Any, principal: Any, grant: Any) -> dict[str, str]:
    """A user holding `rating:read` (Analyst) and `rating:write` (to build the fixtures)."""
    await grant("admin")
    await grant("analyst")
    return {DEV_PRINCIPAL_HEADER: str(principal.id), "Workspace-Id": str(workspace_id)}


@pytest.fixture
def two_versions(
    client: TestClient,
    reader_headers: dict[str, str],
    database: Any,
    blob_store: Any,
    principal: Any,
    workspace_id: Any,
) -> None:
    """Two compiled versions of one algorithm that differ in exactly one step: `s_expr` doubles
    the premium in version 1 and triples it in version 2."""
    register_rating_handlers()
    tripled = _with_adjustment(_minimal_algorithm())
    tripled["version"] = 2
    tripled["steps"][1]["expr"] = "premium_in * 3"
    for version, algorithm in ((1, _with_adjustment(_minimal_algorithm())), (2, tripled)):
        created = client.post("/api/v1/rating-algorithms", json=algorithm, headers=reader_headers)
        assert created.status_code in (200, 201), created.text
        row = asyncio.get_event_loop().run_until_complete(
            _insert_version(
                database,
                workspace_id,
                principal.id,
                algorithm_ref=f"rating_algorithm:minimal@{version}",
                pins=_empty_pins(),
                version=version,
            )
        )
        job = _run_compile_job(client, reader_headers, database, blob_store, row.id)
        assert job.status is JobStatus.SUCCEEDED, job.error


def _run(coro: Any) -> Any:
    return asyncio.get_event_loop().run_until_complete(coro)


async def _set_trace_sample_rate(database: Any, workspace_id: Any, rate: float) -> None:
    async with database.unit_of_work() as session:
        await settings_service.set_workspace_setting(
            session, workspace_id, "rating.trace_sample_rate", rate
        )


def _with_adjustment(algorithm: dict[str, Any]) -> dict[str, Any]:
    """Insert a downstream expression step, so the edit to `s_expr` cascades into `s_adj`. The
    engine traces expression steps only, so `s_adj` is what makes a cascade observable."""
    steps = algorithm["steps"]
    steps.insert(
        2,
        {
            "step_id": "s_adj",
            "type": "expression",
            "label": "Adjust",
            "expr": "payable + 100",
            "result_type": "money_minor",
            "consumes": ["payable"],
            "produces": "adjusted",
        },
    )
    steps[3]["consumes"] = ["adjusted"]
    return algorithm


def _body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "context": {
            "purpose": "new_business",
            "quoted_at": "2026-08-30T09:00:00Z",
            "effective_date": "2026-09-01",
            "inputs": {"premium_in": 1000},
        },
        "base": BASE_REF,
        "comparison": CHANGED_REF,
    }
    body.update(overrides)
    return body


@pytest.mark.req("FR-262")
def test_compare_returns_both_traced_results_and_the_step_diff(
    client: TestClient, reader_headers: dict[str, str], two_versions: None
) -> None:
    response = client.post(COMPARE_URL, json=_body(), headers=reader_headers)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["base"]["outputs"]["payable_premium_minor"] == 2100
    assert body["comparison"]["outputs"]["payable_premium_minor"] == 3100
    assert body["base"]["trace"] is not None
    assert body["comparison"]["trace"] is not None
    steps = body["diff"]["steps"]
    assert [s["step_id"] for s in steps] == ["s_expr", "s_adj"]


@pytest.mark.req("FR-262")
def test_exactly_one_step_is_the_own_change_at_the_http_layer(
    client: TestClient, reader_headers: dict[str, str], two_versions: None
) -> None:
    """RL-1172's one-step proof through the route: the two versions differ only in `s_expr`, so
    exactly that step is an own change and the downstream `s_adj` differs by a moved input."""
    diff = client.post(COMPARE_URL, json=_body(), headers=reader_headers).json()["diff"]

    own = [s["step_id"] for s in diff["steps"] if s["own_change"]]
    assert own == ["s_expr"]
    downstream = [s for s in diff["steps"] if not s["own_change"]]
    assert [s["step_id"] for s in downstream] == ["s_adj"]
    assert "consumed" in downstream[0]["changed_fields"]
    assert diff["unchanged"] == 0


@pytest.mark.req("FR-262")
def test_identical_refs_give_an_empty_diff(
    client: TestClient, reader_headers: dict[str, str], two_versions: None
) -> None:
    """The positive control: a diff that is empty when nothing differs."""
    response = client.post(COMPARE_URL, json=_body(comparison=BASE_REF), headers=reader_headers)

    assert response.status_code == 200, response.text
    assert response.json()["diff"] == {"steps": [], "unchanged": 2}


@pytest.mark.req("FR-262")
def test_a_caller_without_rating_read_is_refused_and_an_anonymous_one_is_401(
    client: TestClient, reader_headers: dict[str, str], two_versions: None
) -> None:
    created = client.post(
        "/api/v1/service-accounts",
        json={"slug": "batch-only-cmp", "environments": ["uat"], "permissions": ["score:batch"]},
        headers=reader_headers,
    )
    assert created.status_code == 201, created.text
    no_read = {
        "X-API-Key": created.json()["key"],
        "Workspace-Id": reader_headers["Workspace-Id"],
    }

    assert client.post(COMPARE_URL, json=_body(), headers=no_read).status_code == 403
    assert client.post(COMPARE_URL, json=_body()).status_code == 401
    assert client.post(COMPARE_URL, json=_body(), headers=reader_headers).status_code == 200


@pytest.mark.req("FR-262")
@pytest.mark.parametrize("side", ["base", "comparison"])
def test_a_ref_naming_no_version_is_a_404_naming_the_side(
    client: TestClient, reader_headers: dict[str, str], two_versions: None, side: str
) -> None:
    response = client.post(
        COMPARE_URL,
        json=_body(**{side: "rating_version:minimal-rv@99"}),
        headers=reader_headers,
    )

    assert response.status_code == 404, response.text
    assert response.json()["detail"].startswith(f"{side}: ")


@pytest.mark.req("FR-262")
@pytest.mark.parametrize("side", ["base", "comparison"])
def test_an_uncompiled_version_is_a_409_naming_the_side(
    client: TestClient,
    reader_headers: dict[str, str],
    database: Any,
    principal: Any,
    workspace_id: Any,
    two_versions: None,
    side: str,
) -> None:
    asyncio.get_event_loop().run_until_complete(
        _insert_version(
            database,
            workspace_id,
            principal.id,
            algorithm_ref="rating_algorithm:minimal@1",
            pins=_empty_pins(),
            version=3,
        )
    )

    response = client.post(
        COMPARE_URL,
        json=_body(**{side: "rating_version:minimal-rv@3"}),
        headers=reader_headers,
    )

    assert response.status_code == 409, response.text
    assert response.json()["code"] == "BUNDLE_COMPILE_FAILED"
    assert response.json()["detail"].startswith(f"{side}: ")


@pytest.mark.req("FR-262")
@pytest.mark.parametrize(("side", "failing_call"), [("base", 0), ("comparison", 1)])
def test_a_per_quote_error_on_one_side_is_a_422_naming_that_side(
    client: TestClient,
    reader_headers: dict[str, str],
    two_versions: None,
    monkeypatch: pytest.MonkeyPatch,
    side: str,
    failing_call: int,
) -> None:
    """DP-S4-5 (a): the other side scores fine, the request still answers 422 with the code."""
    real = score_module.score_one
    calls: list[int] = []

    async def _score_one(*args: Any, **kwargs: Any) -> Any:
        calls.append(1)
        if len(calls) - 1 == failing_call:
            raise CodedError("RATE_TABLE_MISS: no row for the key")
        return await real(*args, **kwargs)

    monkeypatch.setattr(score_module, "score_one", _score_one)
    response = client.post(COMPARE_URL, json=_body(), headers=reader_headers)

    assert response.status_code == 422, response.text
    assert response.json()["code"] == "RATE_TABLE_MISS"
    assert response.json()["detail"] == f"{side}: no row for the key"


@pytest.mark.req("NFR-499")
@pytest.mark.parametrize("failing_call", [0, 1])
def test_a_library_value_error_wearing_a_code_prefix_is_never_a_422_on_compare(
    client: TestClient,
    reader_headers: dict[str, str],
    two_versions: None,
    monkeypatch: pytest.MonkeyPatch,
    failing_call: int,
) -> None:
    """`_as_platform_error` decides by class, not by the shape of the text: a plain `ValueError`
    whose text starts with a per-quote code (a library echoing a value) is a 500 with no text."""
    real = score_module.score_one
    calls: list[int] = []

    async def _score_one(*args: Any, **kwargs: Any) -> Any:
        calls.append(1)
        if len(calls) - 1 == failing_call:
            raise ValueError("RATE_TABLE_MISS: SENTINEL-quote-input-f3")
        return await real(*args, **kwargs)

    monkeypatch.setattr(score_module, "score_one", _score_one)
    response = client.post(COMPARE_URL, json=_body(), headers=reader_headers)

    assert response.status_code == 500, response.text
    assert "SENTINEL-quote-input-f3" not in response.text


@pytest.mark.req("FR-262")
def test_a_context_carrying_its_own_version_ref_is_a_422(
    client: TestClient, reader_headers: dict[str, str], two_versions: None
) -> None:
    body = _body()
    body["context"]["options"] = {"rating_version_ref": BASE_REF}

    response = client.post(COMPARE_URL, json=body, headers=reader_headers)

    assert response.status_code == 422, response.text


async def _persisted_counts(database: Any) -> tuple[int, int]:
    async with database.session() as session:
        traces = await session.execute(select(func.count()).select_from(ScoringTraceRow))
        jobs = await session.execute(select(func.count()).select_from(JobRow))
    return traces.scalar_one(), jobs.scalar_one()


@pytest.mark.req("NFR-499")
def test_compare_persists_nothing_even_at_a_trace_sample_rate_of_one(
    client: TestClient,
    reader_headers: dict[str, str],
    database: Any,
    workspace_id: Any,
    two_versions: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Driven through the route. Two checks, because either alone can pass vacuously:

    - the row counts of `scoring_traces` and `jobs` are unchanged; and
    - `_maybe_sample_trace` is never called. The caller is a user (`rating:read` is not a
      Service Account permission, FR-389), and a user has no `caller.environment`, so a copied
      call raises inside its own `try`, is logged, and writes nothing: the counts alone would
      pass against the defect this guards.
    """
    sampled: list[int] = []

    async def _spy(*_args: Any, **_kwargs: Any) -> None:
        sampled.append(1)

    monkeypatch.setattr(score_module, "_maybe_sample_trace", _spy)
    _run(_set_trace_sample_rate(database, workspace_id, 1.0))
    before = _run(_persisted_counts(database))

    response = client.post(COMPARE_URL, json=_body(), headers=reader_headers)

    assert response.status_code == 200, response.text
    assert sampled == [], "the sandbox route reached FR-259's trace sampling"
    assert _run(_persisted_counts(database)) == before


@pytest.mark.req("NFR-499")
def test_compare_logs_no_input_value(
    client: TestClient,
    reader_headers: dict[str, str],
    two_versions: None,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A sentinel input appears in no record across the HTTP call, and the capture is shown
    non-empty for the same call, so silence is not read from an empty capture."""
    sentinel = "ZZ99 9ZZ"
    body = _body()
    body["context"]["inputs"]["postcode"] = sentinel
    caplog.set_level(logging.DEBUG)

    response = client.post(COMPARE_URL, json=body, headers=reader_headers)

    assert response.status_code == 200, response.text
    assert caplog.records, "the capture is empty, so its silence proves nothing"
    assert sentinel not in caplog.text
    assert sentinel not in " ".join(str(r.__dict__) for r in caplog.records)


@pytest.mark.req("FR-248")
@pytest.mark.parametrize(("side", "failing_call"), [("base", 0), ("comparison", 1)])
def test_a_ladder_that_does_not_reconcile_on_one_side_is_a_500_naming_that_side(
    client: TestClient,
    reader_headers: dict[str, str],
    two_versions: None,
    monkeypatch: pytest.MonkeyPatch,
    side: str,
    failing_call: int,
) -> None:
    """RL-1346 Acceptance 5: the real builder's ladder is planted one minor unit off on one call."""
    from pricing_core.rating import score as core_score

    real = core_score._build_ladder
    calls: list[int] = []

    def off_by_one(inputs: Any, codes: Any) -> Any:
        calls.append(1)
        ladder = real(inputs, codes)
        if len(calls) - 1 == failing_call:
            ladder[-1] = ladder[-1].model_copy(update={"value_minor": ladder[-1].value_minor + 1})
        return ladder

    monkeypatch.setattr(core_score, "_build_ladder", off_by_one)
    response = client.post(COMPARE_URL, json=_body(), headers=reader_headers)

    assert response.status_code == 500, response.text
    assert response.json()["code"] == "LADDER_RECONCILIATION_FAILED"
    assert response.json()["detail"].startswith(f"{side}: ")


@pytest.mark.req("FR-213")
def test_a_context_input_naming_a_produced_value_is_a_422_on_compare(
    client: TestClient, reader_headers: dict[str, str], two_versions: None
) -> None:
    """FD-1425, `/score/compare` (`api/score.py:447`)."""
    body = _body()
    body["context"]["inputs"]["payable"] = 1
    response = client.post(COMPARE_URL, json=body, headers=reader_headers)
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "INPUT_CONTRACT_VIOLATION"
    assert "'payable'" in response.json()["detail"]
