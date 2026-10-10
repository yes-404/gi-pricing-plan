"""The S4 rate-table routes answer 404 `NOT_FOUND` (`03` §5.1, the maintainer's ruling of
2026-10-10 04:19:42), while the shared loaders keep `RATE_TABLE_MISS` for the scoring path."""

from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.api.rate_tables import spec_not_found
from app.errors import PlatformError


@pytest.mark.req("FR-9940")
def test_a_rate_table_miss_is_a_404_not_found_at_the_route() -> None:
    with pytest.raises(PlatformError) as caught, spec_not_found():
        raise PlatformError("RATE_TABLE_MISS", "Rate table not found", 404, "area not found.")
    assert (caught.value.code, caught.value.status_code) == ("NOT_FOUND", 404)
    assert caught.value.detail == "area not found."


@pytest.mark.req("FR-9940")
def test_any_other_error_passes_through_unchanged() -> None:
    with pytest.raises(PlatformError) as caught, spec_not_found():
        raise PlatformError("VALIDATION_FAILED", "Malformed cursor", 400, "bad")
    assert caught.value.code == "VALIDATION_FAILED"


@pytest.mark.req("FR-9940")
@pytest.mark.parametrize("handler", ["read_rate_table", "read_rate_table_cells"])
async def test_the_two_reads_answer_404_not_found_for_an_unknown_table(
    handler: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The maintainer's rulings of 2026-10-10 04:19:42 and 04:23:36: the spec governs, and the
    reads answer 404 `NOT_FOUND`. The handler is called with the service replaced, so no
    database is needed; the loader's `RATE_TABLE_MISS` is what it maps."""
    from app.api import rate_tables as routes

    async def _miss(*_args: object, **_kwargs: object) -> object:
        raise PlatformError("RATE_TABLE_MISS", "Rate table not found", 404, "area not found.")

    monkeypatch.setattr(routes.service, "read_definition", _miss)
    monkeypatch.setattr(routes.service, "cells_page", _miss)
    caller = SimpleNamespace(workspace_id=uuid4())
    calls = {
        "read_rate_table": lambda: routes.read_rate_table("area", 1, caller, None),
        "read_rate_table_cells": lambda: routes.read_rate_table_cells(
            "area", 1, caller, None, None, limit=50, cursor=None
        ),
    }

    with pytest.raises(PlatformError) as caught:
        await calls[handler]()

    assert (caught.value.code, caught.value.status_code) == ("NOT_FOUND", 404)
