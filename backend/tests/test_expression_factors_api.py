"""`POST /factors` and `POST /bandings` for an `expression` Factor (`RL-1615`, `SL-1274`).

`RL-1615`'s Ruled table, "DP-S4-2, creation": a `POST` of an `expression` Factor answers
**422, at the edge**, for four things — a parse error with its position, an undeclared
column (FR-95), a pinned Banding whose `source_expression` differs from the expression, and
an expression that is *certainly numeric* with no `banding_id` (the message names FR-210).
A bare symbol, and a `where`, `min` or `max` at the root, are **not** refused here, because
their type is the column's and only the dataset version can say (that is the resolution
refusal, tested in `pricing-core`).

"Declared" is `source_columns`: FR-95 says the expression is "evaluated over dataset
columns only", and the Factor's declaration of which columns it reads is that field.

The last two tests are `PL-1665` 4.4' (NFR-484): `factor.created` carries `expression` and
`banding.created` carries `source_expression`.

Each is red first, by its cause: today `FactorCreate` is `extra="forbid"` and has no
`expression`, and a `Banding` body with no `column` is refused, so every request is a 422
for the **wrong** reason and the refusal tests' content assertions (the field named, FR-210
in the message) are what fail. The two positive-path tests fail on the 422 itself.
"""

from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest
from backend.tests.test_api_datasets import _headers
from backend.tests.test_model_nfrs import _events, _principal_with
from fastapi.testclient import TestClient

from app.db.session import Database
from app.platform import modelling as model_service
from app.platform import transformations as transform_service
from model_schema import Banding, BandingMethod, Factor, FactorType, new_uuid7


@pytest.fixture
def actuary(workspace_id, principal, grant) -> dict[str, str]:
    asyncio.get_event_loop().run_until_complete(grant("analyst"))
    asyncio.get_event_loop().run_until_complete(grant("pricing_actuary"))
    return _headers(principal.id, workspace_id)


def _factor_body(expression: str, dataset_id: str, **over: object) -> dict[str, object]:
    body: dict[str, object] = {
        "slug": f"expr-{new_uuid7().hex[-6:]}",
        "dataset_id": dataset_id,
        "type": "expression",
        "source_columns": ["driver_age", "vehicle_power"],
        "expression": expression,
    }
    body.update(over)
    return body


def _banding_body(slug: str, dataset_id: str, source_expression: str) -> dict[str, object]:
    return {
        "id": str(new_uuid7()),
        "slug": slug,
        "dataset_id": dataset_id,
        "version": 1,
        "source_expression": source_expression,
        "method": "manual",
        "boundaries": [0.0, 500.0, 1000.0, 9999.0],
        "labels": ["low", "mid", "high"],
        "below_range": "error",
        "above_range": "clamp_to_last",
    }


def _refusal_text(response) -> str:  # type: ignore[no-untyped-def]
    problem = response.json()
    assert problem["code"] == "VALIDATION_FAILED", problem
    return str(problem)


@pytest.mark.req("FR-95")
def test_a_banded_expression_factor_is_created(
    api_client: TestClient, actuary: dict[str, str]
) -> None:
    """The positive path: a Banding over the expression, then the Factor pinning it."""
    dataset_id = str(new_uuid7())
    expression = "driver_age * vehicle_power"
    banding = api_client.post(
        "/api/v1/bandings",
        json=_banding_body(f"b-{new_uuid7().hex[-6:]}", dataset_id, expression),
        headers=actuary,
    )
    assert banding.status_code == 201, banding.text
    assert banding.json()["source_expression"] == expression

    created = api_client.post(
        "/api/v1/factors",
        json=_factor_body(expression, dataset_id, banding_id=banding.json()["id"]),
        headers=actuary,
    )
    assert created.status_code == 201, created.text
    assert created.json()["expression"] == expression
    assert created.json()["type"] == "expression"


@pytest.mark.req("FR-95")
def test_a_parse_error_is_refused_at_creation_with_its_position(
    api_client: TestClient, actuary: dict[str, str]
) -> None:
    refused = api_client.post(
        "/api/v1/factors",
        json=_factor_body("driver_age * (vehicle_power", str(new_uuid7())),
        headers=actuary,
    )
    assert refused.status_code == 422, refused.text
    text = _refusal_text(refused)
    assert "expression" in text
    assert any(word in text.lower() for word in ("position", "column", "col_offset")), text


@pytest.mark.req("FR-95")
def test_an_undeclared_column_is_refused_at_creation(
    api_client: TestClient, actuary: dict[str, str]
) -> None:
    """`vehicle_value` is read by the expression and is not in `source_columns`."""
    refused = api_client.post(
        "/api/v1/factors",
        json=_factor_body("driver_age * vehicle_value", str(new_uuid7())),
        headers=actuary,
    )
    assert refused.status_code == 422, refused.text
    text = _refusal_text(refused)
    assert "vehicle_value" in text, text


@pytest.mark.req("FR-97")
def test_a_pinned_banding_over_another_expression_is_refused_at_creation(
    api_client: TestClient, actuary: dict[str, str]
) -> None:
    dataset_id = str(new_uuid7())
    banding = api_client.post(
        "/api/v1/bandings",
        json=_banding_body(f"b-{new_uuid7().hex[-6:]}", dataset_id, "driver_age * 2"),
        headers=actuary,
    )
    assert banding.status_code == 201, banding.text

    refused = api_client.post(
        "/api/v1/factors",
        json=_factor_body(
            "driver_age * vehicle_power", dataset_id, banding_id=banding.json()["id"]
        ),
        headers=actuary,
    )
    assert refused.status_code == 422, refused.text
    assert "source_expression" in _refusal_text(refused)


@pytest.mark.req("FR-96")
def test_a_factor_version_with_a_changed_expression_cannot_pin_the_old_banding(
    api_client: TestClient, actuary: dict[str, str]
) -> None:
    """Versioning: v2 of a slug, new expression, v1's Banding -> refused at creation."""
    dataset_id = str(new_uuid7())
    expression = "driver_age * vehicle_power"
    banding = api_client.post(
        "/api/v1/bandings",
        json=_banding_body(f"b-{new_uuid7().hex[-6:]}", dataset_id, expression),
        headers=actuary,
    )
    assert banding.status_code == 201, banding.text
    slug = f"expr-{new_uuid7().hex[-6:]}"
    v1 = api_client.post(
        "/api/v1/factors",
        json=_factor_body(expression, dataset_id, slug=slug, banding_id=banding.json()["id"]),
        headers=actuary,
    )
    assert v1.status_code == 201, v1.text

    v2 = api_client.post(
        "/api/v1/factors",
        json=_factor_body(
            "driver_age + vehicle_power", dataset_id, slug=slug, banding_id=banding.json()["id"]
        ),
        headers=actuary,
    )
    assert v2.status_code == 422, v2.text
    assert "source_expression" in _refusal_text(v2)


@pytest.mark.req("FR-95")
@pytest.mark.parametrize(
    "expression",
    [
        "driver_age * vehicle_power",  # arithmetic root
        "driver_age + 1",
        "driver_age ** 2",
        "-driver_age",  # unary minus
        "3.5",  # a numeric literal
        "log(driver_age)",  # a numeric-only function:
        "exp(driver_age)",  # log exp sqrt abs clip log1p expm1
        "sqrt(driver_age)",
        "abs(driver_age)",
        "clip(driver_age, 18, 80)",
        "log1p(driver_age)",
        "expm1(driver_age)",
    ],
)
def test_a_certainly_numeric_expression_without_a_banding_is_refused_naming_fr_210(
    api_client: TestClient, actuary: dict[str, str], expression: str
) -> None:
    refused = api_client.post(
        "/api/v1/factors",
        json=_factor_body(expression, str(new_uuid7())),
        headers=actuary,
    )
    assert refused.status_code == 422, refused.text
    assert "FR-210" in _refusal_text(refused)


@pytest.mark.req("FR-95")
@pytest.mark.parametrize(
    "expression",
    [
        "driver_age",  # a bare symbol: its type is the column's
        "where(driver_age > 40, driver_age, vehicle_power)",
        "min(driver_age, vehicle_power)",
        "max(driver_age, vehicle_power)",
    ],
)
def test_a_not_certainly_numeric_root_is_not_refused_at_creation(
    api_client: TestClient, actuary: dict[str, str], expression: str
) -> None:
    """The guard: creation cannot decide these, so it does not try. Resolution does, by dtype."""
    created = api_client.post(
        "/api/v1/factors",
        json=_factor_body(expression, str(new_uuid7())),
        headers=actuary,
    )
    assert created.status_code == 201, created.text


@pytest.mark.req("FR-83")
@pytest.mark.parametrize(
    "expression", ["driver_age % 2", "driver_age > 40", "frobnicate(driver_age)"]
)
def test_the_grammar_refusals_of_the_factor_profile_reach_the_edge(
    api_client: TestClient, actuary: dict[str, str], expression: str
) -> None:
    """`%`, a bare comparison and an unknown function: 422 with the position (`PL-1621` 4.3)."""
    refused = api_client.post(
        "/api/v1/factors",
        json=_factor_body(expression, str(new_uuid7())),
        headers=actuary,
    )
    assert refused.status_code == 422, refused.text
    text = _refusal_text(refused)
    assert any(word in text.lower() for word in ("position", "column", "col_offset")), text


@pytest.mark.req("NFR-484")
async def test_factor_created_audits_the_expression(database: Database, workspace_id) -> None:
    actor = await _principal_with(database, workspace_id, "analyst", "pricing_actuary")
    factor = Factor(
        id=uuid4(), slug=f"expr-{uuid4().hex[-6:]}", dataset_id=uuid4(), version=1,
        type=FactorType.EXPRESSION, source_columns=("driver_age",),
        expression="where(driver_age > 40, driver_age, 40)",
    )
    async with database.unit_of_work() as session:
        await model_service.create_factor(
            session, workspace_id=workspace_id, actor=actor, factor=factor
        )

    (event,) = await _events(database, workspace_id, "factor.created")
    assert event.after is not None
    assert event.after["expression"] == "where(driver_age > 40, driver_age, 40)"


@pytest.mark.req("NFR-484")
async def test_banding_created_audits_the_source_expression(
    database: Database, workspace_id
) -> None:
    actor = await _principal_with(database, workspace_id, "analyst", "pricing_actuary")
    banding = Banding(
        id=uuid4(), slug=f"b-{uuid4().hex[-6:]}", dataset_id=uuid4(), version=1,
        source_expression="driver_age * 2", method=BandingMethod.MANUAL,
        boundaries=(0.0, 50.0, 100.0), labels=("low", "high"),
    )
    async with database.unit_of_work() as session:
        await transform_service.create_banding(
            session, workspace_id=workspace_id, actor=actor, banding=banding
        )

    (event,) = await _events(database, workspace_id, "banding.created")
    assert event.after is not None
    assert event.after["source_expression"] == "driver_age * 2"
