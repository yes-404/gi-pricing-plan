"""Effective-dated reference lookups (`01` FR-DATA-29, FR-DATA-31).

> A reference lookup is evaluated **as at a declared date** (typically the policy inception
> date), not as at "now".

That distinction is the whole module. A postcode's flood zone, a vehicle's ABI group and an
occupation's code all change over time; rating a 2024 policy with 2026's table produces a
premium that never existed and cannot be reproduced from the policy record. "As at now" is
the default that quietly makes every historical quote unreproducible.

Pure: rows in, value out. The caller loads the pinned Reference Table Version.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date
from typing import Any

__all__ = ["ReferenceLookupError", "lookup_as_at", "resolve_all"]


class ReferenceLookupError(LookupError):
    """No row, or more than one, covers the key at the declared date."""


def lookup_as_at(
    rows: Sequence[Mapping[str, Any]],
    *,
    key: str,
    as_at: date,
    key_field: str = "key",
    from_field: str = "effective_from",
    to_field: str = "effective_to",
) -> Mapping[str, Any] | None:
    """The single row covering `key` at `as_at`, or `None`.

    The interval is **half-open** — `[effective_from, effective_to)` — so a change taking
    effect on the 1st belongs to the new row, not both. A closed interval would make the
    boundary date ambiguous, and the ambiguity would surface as two different premiums for
    the same risk depending on which row was read first.

    More than one match raises rather than picking: the database's exclusion constraint
    should have prevented it, so reaching here means the data came from somewhere that
    constraint does not cover — and silently choosing would hide that.
    """
    matches = [
        row
        for row in rows
        if row[key_field] == key
        and row[from_field] <= as_at
        and (row[to_field] is None or as_at < row[to_field])
    ]
    if not matches:
        return None
    if len(matches) > 1:
        raise ReferenceLookupError(
            f"{len(matches)} reference rows cover {key!r} at {as_at}. Intervals must not "
            "overlap (FR-DATA-29); choosing one silently would hide the overlap and make "
            "the answer depend on row order."
        )
    return matches[0]


def resolve_all(
    keys: Sequence[str],
    rows: Sequence[Mapping[str, Any]],
    *,
    as_at: date,
    **kwargs: Any,
) -> tuple[dict[str, Mapping[str, Any]], tuple[str, ...]]:
    """Resolve many keys, returning the resolved map and the keys that did not resolve.

    Unresolved keys are returned rather than raised: the referential validation layer needs
    the *list* to report, and a lookup that stopped at the first failure would tell an
    actuary about one bad postcode when the feed has four thousand.
    """
    resolved: dict[str, Mapping[str, Any]] = {}
    missing: list[str] = []
    for key in keys:
        row = lookup_as_at(rows, key=key, as_at=as_at, **kwargs)
        if row is None:
            missing.append(key)
        else:
            resolved[key] = row
    return resolved, tuple(missing)
