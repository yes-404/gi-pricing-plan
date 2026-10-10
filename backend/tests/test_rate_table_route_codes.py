"""The S4 rate-table routes answer 404 `NOT_FOUND` (`03` §5.1, the maintainer's ruling of
2026-10-10 04:19:42), while the shared loaders keep `RATE_TABLE_MISS` for the scoring path."""

from __future__ import annotations

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
