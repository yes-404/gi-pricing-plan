"""Effective-dated reference lookups (`01` FR-DATA-29, FR-DATA-31)."""

from __future__ import annotations

from datetime import date

import pytest

from pricing_core.data.reference import ReferenceLookupError, lookup_as_at, resolve_all

ROWS = [
    {"key": "SW1A", "payload": {"zone": "3"}, "effective_from": date(2024, 1, 1),
     "effective_to": date(2026, 1, 1)},
    {"key": "SW1A", "payload": {"zone": "2"}, "effective_from": date(2026, 1, 1),
     "effective_to": None},
    {"key": "EC1A", "payload": {"zone": "1"}, "effective_from": date(2024, 1, 1),
     "effective_to": None},
]


@pytest.mark.req("FR-DATA-31")
def test_a_lookup_is_evaluated_as_at_the_declared_date() -> None:
    """Rating a 2024 policy with 2026's table produces a premium that never existed and
    cannot be reproduced from the policy record."""
    old = lookup_as_at(ROWS, key="SW1A", as_at=date(2025, 6, 1))
    new = lookup_as_at(ROWS, key="SW1A", as_at=date(2026, 6, 1))
    assert old["payload"]["zone"] == "3"
    assert new["payload"]["zone"] == "2"


@pytest.mark.req("FR-DATA-29")
def test_the_interval_is_half_open_so_the_boundary_belongs_to_the_new_row() -> None:
    """A closed interval would make the boundary date ambiguous, and the ambiguity would
    surface as two different premiums for the same risk."""
    assert lookup_as_at(ROWS, key="SW1A", as_at=date(2026, 1, 1))["payload"]["zone"] == "2"


@pytest.mark.req("FR-DATA-29")
def test_an_open_ended_row_covers_every_later_date() -> None:
    assert lookup_as_at(ROWS, key="EC1A", as_at=date(2030, 1, 1)) is not None


@pytest.mark.req("FR-DATA-31")
def test_a_date_before_any_row_resolves_to_nothing() -> None:
    """Negative: returning the earliest row would silently rate a policy against a table
    that did not exist when it incepted."""
    assert lookup_as_at(ROWS, key="SW1A", as_at=date(2020, 1, 1)) is None


@pytest.mark.req("FR-DATA-29")
def test_overlapping_rows_raise_rather_than_choosing() -> None:
    """The database constraint should have prevented this, so reaching here means the data
    came from somewhere it does not cover — and choosing silently would hide that."""
    overlapping = [
        {"key": "K", "payload": {}, "effective_from": date(2026, 1, 1),
         "effective_to": date(2026, 12, 1)},
        {"key": "K", "payload": {}, "effective_from": date(2026, 6, 1),
         "effective_to": None},
    ]
    with pytest.raises(ReferenceLookupError, match="must not"):
        lookup_as_at(overlapping, key="K", as_at=date(2026, 7, 1))


@pytest.mark.req("FR-DATA-29")
def test_resolve_all_reports_every_unresolved_key() -> None:
    """A lookup that stopped at the first failure would tell an actuary about one bad
    postcode when the feed has four thousand."""
    resolved, missing = resolve_all(
        ["SW1A", "NOPE", "EC1A", "ALSO-NOPE"], ROWS, as_at=date(2026, 6, 1)
    )
    assert set(resolved) == {"SW1A", "EC1A"}
    assert missing == ("NOPE", "ALSO-NOPE")
