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
import re
import uuid
from uuid import uuid4

import pytest
from backend.tests.test_api_datasets import _headers
from backend.tests.test_model_nfrs import _events, _principal_with
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.config import Settings
from app.db.models import AuditEventRow, BandingRow, ModelRow
from app.db.session import Database
from app.platform import modelling as model_service
from app.platform import transformations as transform_service
from model_schema import (
    Banding,
    BandingMethod,
    Factor,
    FactorType,
    GlmSpec,
    ModelStatus,
    OffsetSpec,
    new_uuid7,
)


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


class _RollBack(Exception):
    """Raised inside a unit of work to end it by rolling back, never by committing.

    A Banding over an expression has a NULL `column_name`. Such a row, once committed, stays in
    the shared test database for as long as the schema does (and an old build cannot read it),
    so the tests that need one assert inside the transaction and then roll it back.
    """


async def _events_in_session(session, workspace_id, action: str):  # type: ignore[no-untyped-def]
    """The Audit Events one action wrote **in this open transaction** (not yet committed)."""
    return list(
        (
            await session.execute(
                select(AuditEventRow).where(
                    AuditEventRow.workspace_id == workspace_id,
                    AuditEventRow.action == action,
                )
            )
        )
        .scalars()
        .all()
    )


def _assert_positioned(  # type: ignore[no-untyped-def]
    response, column: int | None = None, names: str | None = None
) -> None:
    """`RL-1700` (b): one `FieldError` on `expression`, `VALIDATION_FAILED`, positioned.

    `RL-1362` DP-S3-3 item 1's form: a message that begins `line <L>, column <C>:`. The
    column is asserted exactly only where the ruling fixes one (`column` is 1-based).
    """
    problem = response.json()
    assert problem["code"] == "VALIDATION_FAILED", problem
    errors = problem["errors"]
    assert len(errors) == 1, problem
    assert errors[0]["field"] == "expression", problem
    assert errors[0]["code"] == "VALIDATION_FAILED", problem
    message = errors[0]["message"]
    assert re.match(r"^line \d+, column \d+: ", message), problem
    if column is not None:
        assert message.startswith(f"line 1, column {column}: "), problem
    if names is not None:
        assert names in message, problem


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
    _assert_positioned(refused)  # form only: the SyntaxError offset is CPython's (RL-1700 (b))


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
    _assert_positioned(refused, column=14, names="vehicle_value")


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
def test_a_binop_root_over_strings_is_still_refused_as_certainly_numeric(
    api_client: TestClient, actuary: dict[str, str]
) -> None:
    """`DP-1274-NUMERIC` (a), ruled 2026-10-16 10:27:41 BST: pinned, not accidental.

    `region + alt_region` is a string concatenation in polars, but `is_certainly_numeric`
    treats every arithmetic root as a number, which is FR-95's literal wording. The 422 is
    over-refusal, and fail-safe: it never misprices. Whether the operands should be typed
    first is an open question (the OQ for option (b)), not this test's.
    """
    refused = api_client.post(
        "/api/v1/factors",
        json=_factor_body(
            "region + alt_region",
            str(new_uuid7()),
            source_columns=["region", "alt_region"],
        ),
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
    ("expression", "column"),
    [
        ("driver_age % 2", None),
        ("driver_age > 40", None),
        ("frobnicate(driver_age)", None),
        ("driver_age * 2 + frobnicate(driver_age)", 18),
    ],
)
def test_the_grammar_refusals_of_the_factor_profile_reach_the_edge(
    api_client: TestClient, actuary: dict[str, str], expression: str, column: int | None
) -> None:
    """`%`, a bare comparison and an unknown function: 422 with the position (`PL-1621` 4.3)."""
    refused = api_client.post(
        "/api/v1/factors",
        json=_factor_body(expression, str(new_uuid7())),
        headers=actuary,
    )
    assert refused.status_code == 422, refused.text
    _assert_positioned(refused, column=column)


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
    # Asserted inside the transaction, which is then rolled back: the Banding's row has a NULL
    # `column_name` and must never be committed (see `_RollBack`).
    with pytest.raises(_RollBack):
        async with database.unit_of_work() as session:
            await transform_service.create_banding(
                session, workspace_id=workspace_id, actor=actor, banding=banding
            )
            (event,) = await _events_in_session(session, workspace_id, "banding.created")
            assert event.after is not None
            assert event.after["source_expression"] == "driver_age * 2"
            raise _RollBack

    assert await _events(database, workspace_id, "banding.created") == []


def _seed_fitted_model(workspace_id, slug: str, factor_ids: list[str]) -> None:  # type: ignore[no-untyped-def]
    """A `fitted` Model whose spec pins `factor_ids`, on a loop of our own (`test_api_models`)."""
    from backend.tests.conftest_db import test_database_url

    spec = GlmSpec(
        model_family_slug=slug,
        dataset_version_id=new_uuid7(),
        response_column="claim_count",
        offset=OffsetSpec(kind="log_column", column="exposure_years"),
        factors=tuple(uuid.UUID(f) for f in factor_ids),
    )

    async def _insert(database: Database) -> None:
        async with database.unit_of_work() as session:
            session.add(
                ModelRow(
                    workspace_id=workspace_id,
                    model_family_slug=slug,
                    version=1,
                    status=ModelStatus.FITTED.value,
                    dataset_version_id=spec.dataset_version_id,
                    spec=spec.model_dump(mode="json"),
                    spec_hash=f"v3:sha256:{new_uuid7().hex}{new_uuid7().hex}",
                )
            )

    loop = asyncio.new_event_loop()
    try:
        database = Database(Settings(database_url=test_database_url()))
        try:
            loop.run_until_complete(_insert(database))
        finally:
            loop.run_until_complete(database.dispose())
    finally:
        loop.close()


@pytest.mark.req("FR-96")
def test_a_fitted_models_pin_returns_the_posted_expression_and_a_new_version_does_not_move_it(
    api_client: TestClient, actuary: dict[str, str], workspace_id
) -> None:
    """`PL-1665` 4.7 / `RL-1700` DP 4.7 (C'): the chain, not a copy of the field.

    The Model's factor record is the Factor version its spec pins. Step 4 is what makes this
    evidence rather than a lookup: a pin that followed the slug would pass steps 1-3.
    """
    dataset_id = str(new_uuid7())
    expression = "driver_age * vehicle_power"
    slug = f"expr-{new_uuid7().hex[-6:]}"
    band_slug = f"b-{new_uuid7().hex[-6:]}"

    def _banded(expr: str) -> str:
        made = api_client.post(
            "/api/v1/bandings", json=_banding_body(band_slug, dataset_id, expr), headers=actuary
        )
        assert made.status_code == 201, made.text
        return str(made.json()["id"])

    v1 = api_client.post(
        "/api/v1/factors",
        json=_factor_body(expression, dataset_id, slug=slug, banding_id=_banded(expression)),
        headers=actuary,
    )
    assert v1.status_code == 201, v1.text

    # 1. A fitted Model whose spec pins that Factor version.
    family = f"fam-{new_uuid7().hex[-6:]}"
    _seed_fitted_model(workspace_id, family, [v1.json()["id"]])

    # 2. The Model names the id.
    model = api_client.get(f"/api/v1/models/{family}", headers=actuary)
    assert model.status_code == 200, model.text
    assert v1.json()["id"] in model.json()["spec"]["factors"]

    def _pinned_expression() -> str:
        listed = api_client.get(f"/api/v1/factors?dataset_id={dataset_id}", headers=actuary)
        assert listed.status_code == 200, listed.text
        (pinned,) = [f for f in listed.json() if f["id"] == v1.json()["id"]]
        return str(pinned["expression"])

    # 3. The pinned Factor carries the text that was posted.
    assert _pinned_expression() == expression

    # 4. A version 2 with another expression has another id and does not move the pin.
    changed = "driver_age + vehicle_power"
    v2 = api_client.post(
        "/api/v1/factors",
        json=_factor_body(changed, dataset_id, slug=slug, banding_id=_banded(changed)),
        headers=actuary,
    )
    assert v2.status_code == 201, v2.text
    assert v2.json()["id"] != v1.json()["id"]
    assert v2.json()["expression"] == changed
    assert _pinned_expression() == expression


@pytest.mark.req("FR-101")
async def test_the_orm_and_the_migrated_column_agree_that_column_name_is_nullable(
    database: Database, workspace_id
) -> None:
    """`RL-1700` (c) and the maintainer's 09:51:01 condition 1.

    A Banding cut over an expression has no column. If the ORM said NOT NULL while the
    migration dropped it (or the reverse), this insert would fail at the ORM or at the
    database. It runs against the migrated schema, so it fails if either side disagrees.
    """
    assert BandingRow.__table__.c.column_name.nullable is True
    # The flush is what meets the migrated schema (an `IntegrityError` there is the database
    # saying NOT NULL); the transaction is then rolled back, so no NULL row is ever committed.
    with pytest.raises(_RollBack):
        async with database.unit_of_work() as session:
            session.add(
                BandingRow(
                    workspace_id=workspace_id,
                    dataset_id=uuid4(),
                    slug=f"b-{uuid4().hex[-6:]}",
                    version=1,
                    column_name=None,
                    body={},
                )
            )
            await session.flush()
            raise _RollBack
