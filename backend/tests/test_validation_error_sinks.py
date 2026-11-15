"""A validation failure's text reaching a caller or a log carries no submitted value (NFR-499).

FD-1589 / #1712 rows 2, 3, 7, 9 and 10 (rows 4, 5 and 6 are S7b's): each sink used to render
`str(exc)` (or `f"{exc}"`) of a Pydantic `ValidationError` or a library error, and that text
prints every failing `input_value`.
Each now goes through `pricing_core.safe_error.safe_error_detail` (or fixed text, or `from None`).
Every test plants a sentinel where the sink can see it and asserts the sentinel is absent, with a
control that the text a caller needs is still there. Row 3's plain `ValueError` is a planted
reach, not a live one: the record says its reach is not demonstrated.
"""

from __future__ import annotations

import asyncio
import traceback
from contextlib import asynccontextmanager
from types import SimpleNamespace
from uuid import uuid4

import pytest
from backend.tests.test_prediction import _fitted_glm
from backend.tests.test_rating_version_compile import _empty_pins, _headers, _minimal_algorithm

from app.config import ConfigInvalidError, load_settings
from app.db.models import RatingAlgorithmRow
from app.errors import PlatformError
from app.platform import prediction as prediction_service
from app.platform import rate_tables as rate_tables_service

_SENTINEL = "SENTINEL-submitted-value-4f8a21"


@pytest.mark.req("NFR-499")
async def test_a_bulk_operation_parameter_refusal_carries_no_submitted_value(monkeypatch) -> None:
    """Row 2: `bulk_operation`'s `except ValidationError` clause."""

    class _Session:
        async def scalar(self, _statement):
            return SimpleNamespace(id=uuid4())

    class _Database:
        @asynccontextmanager
        async def unit_of_work(self):
            yield _Session()

    async def _load_version(*_args):
        return SimpleNamespace()

    async def _to_version(*_args):
        return None

    monkeypatch.setattr(rate_tables_service, "_load_version", _load_version)
    monkeypatch.setattr(rate_tables_service, "_to_version", _to_version)

    with pytest.raises(PlatformError) as refused:
        await rate_tables_service.bulk_operation(
            _Database(), uuid4(), SimpleNamespace(id=uuid4()), None, None,
            slug="t", version=1, kind="uplift_table", parameters={"percentage": _SENTINEL},
        )
    assert refused.value.status_code == 422
    assert refused.value.code == "VALIDATION_FAILED"
    assert "percentage" in (refused.value.detail or ""), "control: the field is still named"
    assert _SENTINEL not in (refused.value.detail or "")


@pytest.mark.req("NFR-499")
def test_a_library_value_error_in_a_bulk_operation_carries_no_value() -> None:
    """Row 3, a PLANTED reach: the fallback of `_map_operation_error` for a plain `ValueError`
    whose text repeats a value. A coded refusal keeps its detail (control)."""
    fallback = rate_tables_service._map_operation_error(ValueError(f"cannot read {_SENTINEL}"))
    assert fallback.code == "VALIDATION_FAILED"
    assert _SENTINEL not in (fallback.detail or "")

    coded = rate_tables_service._map_operation_error(
        ValueError("INCOMPLETE_KEY_DOMAIN: key a is missing")
    )
    assert coded.code == "RATE_TABLE_INCOMPLETE"
    assert coded.detail == "key a is missing"


@pytest.mark.req("NFR-499")
def test_a_stored_algorithm_that_no_longer_validates_leaks_no_value_at_version_create(
    api_client, workspace_id, principal, grant, database
) -> None:
    """Row 7: the second `except ValueError` clause of `create_rating_version`. The code is
    kept (Q2 (a)); the text is the allow-listed one."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(grant("analyst"))
    headers = _headers(principal, workspace_id)
    stored = _minimal_algorithm()
    stored["steps"][0]["type"] = _SENTINEL

    # A saved algorithm is an immutable artifact (no UPDATE, even for the owner), so the stale
    # row is INSERTed already invalid: what an older validator once accepted and the current one
    # refuses. The same direct write `test_rating_version_dislocation_gate` makes.
    async def _store() -> None:
        async with database.unit_of_work() as session:
            session.add(
                RatingAlgorithmRow(
                    workspace_id=workspace_id, slug="minimal", version=1,
                    content=stored, created_by=principal.id,
                )
            )

    loop.run_until_complete(_store())

    refused = api_client.post(
        "/api/v1/rating-versions",
        json={
            "slug": "stale-algorithm-rv",
            "dataset_version_id": str(uuid4()),
            "model_ref": "model:motor-ad-frequency@7",
            "algorithm_ref": "rating_algorithm:minimal@1",
            "pins": _empty_pins(),
        },
        headers=headers,
    )
    assert refused.status_code == 422, refused.text
    assert refused.json()["code"] == "MODEL_REFERENCE_MODE_INCONSISTENT"
    assert _SENTINEL not in refused.text


@pytest.mark.req("NFR-499")
@pytest.mark.parametrize(
    "setting", ["job_stall_seconds"], ids=["an invalid GIP_ setting"]
)
def test_a_refused_configuration_carries_no_value_in_its_traceback(setting: str) -> None:
    """Row 9: `load_settings` raises `from None`, so the chained `ValidationError`, which prints
    `input_value`, is not in any traceback. The per-field line is kept (control)."""
    with pytest.raises(ConfigInvalidError) as refused:
        load_settings(**{setting: _SENTINEL})
    rendered = "".join(traceback.format_exception(refused.value))
    assert f"GIP_{setting.upper()}" in rendered, "control: the variable is still named"
    assert _SENTINEL not in rendered


@pytest.mark.req("NFR-499")
async def test_a_body_that_is_not_a_table_carries_no_polars_text(
    database, blob_store, workspace_id
) -> None:
    """Row 10: `predict_rows`' detail is fixed text, with none of polars' own message."""
    actor, model_id = await _fitted_glm(database, blob_store, workspace_id)

    # The model and its factors resolve (FR-87); the body is the fault. A non-mapping first row
    # makes `pl.DataFrame` raise a `TypeError` whose text prints the next row's value.
    async with database.session() as session:
        with pytest.raises(PlatformError) as refused:
            await prediction_service.predict_rows(
                session,
                workspace_id=workspace_id,
                actor=actor,
                model_id=model_id,
                rows=["urban", {"area": _SENTINEL}],  # type: ignore[list-item]
                blob_store=blob_store,
            )
    assert refused.value.status_code == 422
    assert refused.value.code == "VALIDATION_FAILED"
    assert "same columns" in (refused.value.detail or ""), "control: the guidance is kept"
    assert _SENTINEL not in (refused.value.detail or "")
