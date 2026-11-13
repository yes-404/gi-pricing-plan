"""FD-1671 / SL-8432: the score routes refuse what pricing-core refuses (FR-273).

A decimal Rating Input is a JSON number on the wire. Starlette parses it to a `float`, so a
text of more than about 15 significant digits was rounded *before* pricing-core's FR-273
guard (`_engine_context`: lossless as a float, else refused by name) could see it, and
`POST /score` answered 200 with the premium of the rounded value. The ruled design (the
maintainer's (by delegation) "2026-11-13 19:53:34 GMT" (R2), design (b)) parses the JSON numbers
of the scoring routes' bodies as `Decimal`, so the one definition is core's.

No database: the route is the real `app.api.score` router on a bare app with the app's real error
handlers, its auth, rate-limit, session and resolution dependencies stubbed (the probe's harness,
`scratch/exec-fd1671p/probe.md`). The create_app()+DB reading is
`test_score_decimal_input_db.py`.

Exact references are computed from the request text with `decimal`, never from a parsed float.
"""

from __future__ import annotations

import asyncio
import types
import typing
from collections.abc import Iterator
from decimal import ROUND_HALF_EVEN, Decimal, localcontext
from typing import Any
from uuid import uuid4

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

from app.api import deps as deps_module
from app.api import score as score_module
from app.errors import install_error_handlers
from model_schema import RatingVersion
from pricing_core.rating.compile import ResolvedArtifact, compile_bundle
from pricing_core.rating.runtime import CompiledBundle, load_bundle

SCORE_URL = "/api/v1/score"
COMPARE_URL = "/api/v1/score/compare"
REF = "rating_version:score-fixture@1"

_ALGORITHM: dict[str, Any] = {
    "slug": "score-fixture",
    "version": 1,
    "input_contract": [
        {"name": "base_minor", "type": "int", "nullable": False},
        {"name": "factor", "type": "decimal", "nullable": False},
    ],
    "outputs": [{"name": "payable_premium_minor", "type": "money_minor", "required": True}],
    "steps": [
        {
            "step_id": "s_in_b",
            "type": "input",
            "label": "b",
            "input_name": "base_minor",
            "on_missing": "error",
            "produces": "base_minor",
        },
        {
            "step_id": "s_in_f",
            "type": "input",
            "label": "f",
            "input_name": "factor",
            "on_missing": "error",
            "produces": "factor",
        },
        {
            "step_id": "s_x",
            "type": "expression",
            "label": "x",
            "expr": "base_minor * factor",
            "result_type": "money_minor",
            "consumes": ["base_minor", "factor"],
            "produces": "premium_minor",
        },
        {
            "step_id": "s_out",
            "type": "output",
            "label": "o",
            "output_name": "payable_premium_minor",
            "rounding": {"mode": "half_even", "dp": 0},
            "consumes": ["premium_minor"],
        },
    ],
    "sub_graphs": [],
}


class _Resolver:
    async def resolve(self, ref: Any) -> ResolvedArtifact:
        return ResolvedArtifact(status="approved", payload=_ALGORITHM)


def _version() -> RatingVersion:
    return RatingVersion.model_validate(
        {
            "id": str(uuid4()),
            "workspace_id": str(uuid4()),
            "slug": "score-fixture",
            "version": 1,
            "status": "draft",
            "dataset_version_id": str(uuid4()),
            "model_ref": "model:none@1",
            "created_at": "2026-08-29T12:00:00Z",
            "created_by": str(uuid4()),
            "updated_at": "2026-08-29T12:00:00Z",
            "algorithm_ref": "rating_algorithm:score-fixture@1",
            "pins": {
                "rate_tables": [],
                "models": [],
                "reference_tables": [],
                "custom_objectives": [],
            },
            "model_reference_mode": "exact",
        }
    )


def _exact_minor(base: int, text: str) -> int:
    """The price of `base * text`, rounded half-even once, from the TEXT (never a float)."""
    with localcontext() as ctx:
        ctx.prec = 80
        return int((Decimal(base) * Decimal(text)).quantize(Decimal(1), rounding=ROUND_HALF_EVEN))


@pytest.fixture(scope="module")
def compiled() -> CompiledBundle:
    return load_bundle(asyncio.run(compile_bundle(_version(), _Resolver())))


@pytest.fixture
def seen(compiled: CompiledBundle, monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    """The `inputs` each `score_one` call received, in order."""
    calls: list[dict[str, Any]] = []
    real = score_module.score_one

    async def spy(bundle: Any, ctx: Any, **kwargs: Any) -> Any:
        calls.append(dict(ctx.inputs))
        return await real(bundle, ctx, **kwargs)

    async def no_route(*_a: Any, **_k: Any) -> None:
        return None

    async def held(*_a: Any, **_k: Any) -> CompiledBundle:
        return compiled

    async def no_sample(*_a: Any, **_k: Any) -> None:
        return None

    monkeypatch.setattr(score_module, "score_one", spy)
    monkeypatch.setattr(score_module, "_routed", no_route)
    monkeypatch.setattr(score_module, "_compiled_for", held)
    monkeypatch.setattr(score_module, "_maybe_sample_trace", no_sample)
    return calls


@pytest.fixture
def client(seen: list[dict[str, Any]]) -> Iterator[TestClient]:
    app = FastAPI()
    install_error_handlers(app)
    app.include_router(score_module.router, prefix="/api/v1")
    # A throwaway route outside the scoring routes: it must keep parsing JSON numbers as float.
    echo = APIRouter()

    @echo.post("/echo")
    async def _echo(body: dict[str, object]) -> dict[str, str]:
        return {k: type(v).__name__ for k, v in body.items()}

    app.include_router(echo, prefix="/api/v1")
    caller = types.SimpleNamespace(workspace_id=uuid4(), environment=None)
    overrides = app.dependency_overrides
    overrides[typing.get_args(score_module.ScoreExecuteDep)[1].dependency] = lambda: caller
    overrides[typing.get_args(score_module.RatingReadDep)[1].dependency] = lambda: caller
    overrides[score_module._enforce_score_rate_limit] = lambda: None
    overrides[deps_module.request_session] = lambda: None
    overrides[deps_module._settings] = lambda: None
    for dependency in (
        score_module._database,
        score_module._blob_store,
        score_module._bundle_slot,
        score_module._live_refs,
    ):
        overrides[dependency] = lambda: None
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


def _body(base: int, factor_text: str, extra_inputs: str = "") -> str:
    """A raw request body: the factor is written as a JSON number, character for character."""
    return (
        '{"purpose":"new_business","quoted_at":"2026-08-29T12:00:00",'
        '"effective_date":"2026-09-01",'
        f'"inputs":{{"base_minor":{base},"factor":{factor_text}{extra_inputs}}},'
        f'"options":{{"rating_version_ref":"{REF}"}}}}'
    )


def _compare_body(base: int, factor_text: str) -> str:
    return (
        '{"base":"rating_version:score-fixture@1","comparison":"rating_version:score-fixture@2",'
        '"context":{"purpose":"new_business","quoted_at":"2026-08-29T12:00:00",'
        '"effective_date":"2026-09-01",'
        f'"inputs":{{"base_minor":{base},"factor":{factor_text}}}}}}}'
    )


def _post(client: TestClient, url: str, body: str) -> Any:
    return client.post(url, content=body, headers={"content-type": "application/json"})


def _assert_refused_naming_the_input(response: Any, factor_text: str) -> None:
    assert response.status_code == 422, response.text
    assert response.headers["content-type"].startswith("application/problem+json")
    problem = response.json()
    assert problem["code"] == "INPUT_CONTRACT_VIOLATION"
    assert "'factor'" in problem["detail"]
    assert factor_text not in response.text  # NFR-499: the problem carries no quote value


# --- condition (a): the reading of record, I1 to I3 -----------------------------------------

I2_TEXT = "0.82469000000000000002"  # 20 significant digits: exact price 41235, float price 41234
I3_TEXT = "0.82468999999999999998"  # 20 significant digits: parses to the same float as I2
I1_TEXT = "0.824690000000000"  # 15 significant digits: the float is exact for the purpose


@pytest.mark.req("FR-273")
def test_i2_a_20_digit_decimal_input_is_refused_not_rounded_and_priced(client: TestClient) -> None:
    assert _exact_minor(50000, I2_TEXT) == 41235
    _assert_refused_naming_the_input(_post(client, SCORE_URL, _body(50000, I2_TEXT)), I2_TEXT)


@pytest.mark.req("FR-273")
def test_i3_a_20_digit_decimal_input_below_the_rounding_boundary_is_refused_too(
    client: TestClient,
) -> None:
    _assert_refused_naming_the_input(_post(client, SCORE_URL, _body(50000, I3_TEXT)), I3_TEXT)


@pytest.mark.req("FR-239")
def test_i1_a_15_digit_decimal_input_still_prices_as_before(client: TestClient) -> None:
    response = _post(client, SCORE_URL, _body(50000, I1_TEXT))
    assert response.status_code == 200, response.text
    assert response.json()["outputs"]["payable_premium_minor"] == 41234
    assert _exact_minor(50000, I1_TEXT) == 41234


# --- condition (b): every scoring path ------------------------------------------------------


@pytest.mark.req("FR-273")
@pytest.mark.parametrize("text", [I2_TEXT, I3_TEXT])
def test_compare_refuses_an_over_precision_input_and_names_the_side(
    client: TestClient, text: str
) -> None:
    response = _post(client, COMPARE_URL, _compare_body(50000, text))
    assert response.status_code == 422, response.text
    assert response.headers["content-type"].startswith("application/problem+json")
    problem = response.json()
    assert problem["code"] == "INPUT_CONTRACT_VIOLATION"
    assert problem["detail"].startswith("base: ")  # the first side to fail is named (DP-S4-5)
    assert "'factor'" in problem["detail"]
    assert text not in response.text


@pytest.mark.req("FR-239")
def test_compare_still_prices_a_15_digit_input(client: TestClient) -> None:
    response = _post(client, COMPARE_URL, _compare_body(50000, I1_TEXT))
    assert response.status_code == 200, response.text
    assert response.json()["base"]["outputs"]["payable_premium_minor"] == 41234


@pytest.mark.req("FR-273")
def test_the_batch_route_takes_no_rating_input_over_json() -> None:
    """`POST /score/batch` carries a Dataset Version id and Rating Version refs, never a
    Rating Input: its rows are read from the Dataset Version's table by the Job handler
    (`app.worker.scoring_handlers`), so no JSON number reaches `ctx.inputs` through it."""
    fields = set(score_module.BatchScoreRequest.model_fields)
    assert fields == {
        "dataset_version_id",
        "rating_version_refs",
        "table_name",
        "chunk_rows",
        "abort_failure_rate",
    }


# --- condition (d): the hook is scoped to the scoring routes --------------------------------


@pytest.mark.req("FR-273")
def test_a_route_outside_the_scoring_routes_still_parses_a_json_number_as_float(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/echo",
        content='{"x": 0.82469000000000000002, "n": 3, "s": "a", "b": true}',
        headers={"content-type": "application/json"},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {"x": "float", "n": "int", "s": "str", "b": "bool"}


@pytest.mark.req("FR-273")
def test_the_batch_route_keeps_the_default_route_class() -> None:
    batch = next(r for r in score_module.router.routes if getattr(r, "path", "") == "/score/batch")
    assert type(batch).__name__ == "APIRoute"


# --- condition (e): ints, bools and strings are untouched -----------------------------------


@pytest.mark.req("FR-273")
def test_ints_bools_and_strings_reach_the_engine_as_themselves(
    client: TestClient, seen: list[dict[str, Any]]
) -> None:
    extra = ',"a_flag":true,"a_note":"x","a_count":7'
    response = _post(client, SCORE_URL, _body(50000, "0.75", extra))
    assert response.status_code == 200, response.text
    inputs = seen[-1]
    assert inputs["base_minor"] == 50000
    assert type(inputs["base_minor"]) is int
    assert inputs["a_flag"] is True
    assert inputs["a_note"] == "x"
    assert type(inputs["a_count"]) is int


@pytest.mark.req("FR-273")
def test_an_exactly_representable_decimal_input_prices_as_before(client: TestClient) -> None:
    response = _post(client, SCORE_URL, _body(50000, "0.75"))
    assert response.status_code == 200, response.text
    assert response.json()["outputs"]["payable_premium_minor"] == 37500


@pytest.mark.req("FR-273")
def test_a_non_decimal_input_given_a_json_float_behaves_as_before(client: TestClient) -> None:
    """`base_minor` is declared `int`: a JSON `50000.0` was a float, refused as not an int; as a
    Decimal it is refused for the same reason, by the same code."""
    response = _post(
        client,
        SCORE_URL,
        _body(50000, "0.75").replace('"base_minor":50000', '"base_minor":50000.0'),
    )
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "INPUT_CONTRACT_VIOLATION"
    assert "'base_minor'" in response.json()["detail"]


@pytest.mark.req("FR-273")
def test_an_undeclared_float_input_is_tolerated_as_before(client: TestClient) -> None:
    """`_validate_inputs` tolerates extra keys, and they cross into the engine context as the
    float the JSON path always delivered: a Decimal there would be a binding `TypeError`."""
    response = _post(client, SCORE_URL, _body(50000, "0.75", ',"extra_rate":1.5'))
    assert response.status_code == 200, response.text
    assert response.json()["outputs"]["payable_premium_minor"] == 37500
