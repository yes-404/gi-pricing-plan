"""Every counted `/api/v1` operation declares `429` (`RL-1687`; the lead's ruling "2026-10-16
10:30:18 BST", concurred by the maintainer (by delegation) at 10:30:57 BST; WK-674 Slice 4).

The management rate limit makes these routes return `429 RATE_LIMITED`; an undeclared status is
the drift `RL-1347` rule 4 closed for `/score`. One router-level mechanism declares it (`app.main`
`counted()`), so this test walks the assembled OpenAPI document and holds the whole set, rather
than one route per test. Excluded: `GET /api/v1/auth/config` (unauthenticated, never counted) and
the `/score` family (under the scoring limit; `POST /score` declares its own `429`).
"""

from __future__ import annotations

from typing import Any

import pytest

API_PREFIX = "/api/v1"
_METHODS = frozenset({"get", "put", "post", "delete", "options", "head", "patch", "trace"})
_EXCLUDED_PATHS = frozenset({f"{API_PREFIX}/auth/config"})
_SCORE_FAMILY = f"{API_PREFIX}/score"


def _is_excluded(path: str) -> bool:
    return path in _EXCLUDED_PATHS or path == _SCORE_FAMILY or path.startswith(f"{_SCORE_FAMILY}/")


@pytest.fixture(scope="module")
def document() -> dict[str, Any]:
    from app.config import Environment, Settings
    from app.main import create_app

    document: dict[str, Any] = create_app(
        Settings(environment=Environment.LOCAL, version="test")
    ).openapi()
    return document


@pytest.mark.req("FR-452")
def test_every_counted_api_operation_declares_429(document: dict[str, Any]) -> None:
    """Red when the router-level mechanism is removed from `app.main`: the first operation
    without a `429` response is named in the failure."""
    counted = sorted(
        (path, method)
        for path, item in document["paths"].items()
        if path.startswith(f"{API_PREFIX}/") and not _is_excluded(path)
        for method in item
        if method in _METHODS
    )
    assert counted, "no /api/v1 operation was found: the walk is vacuous"
    missing = [
        f"{method.upper()} {path}"
        for path, method in counted
        if "429" not in document["paths"][path][method].get("responses", {})
    ]
    assert not missing, (
        f"{len(missing)} of {len(counted)} counted operations do not declare 429; "
        f"first: {missing[0]}"
    )


@pytest.mark.req("FR-452")
def test_the_429_exclusions_are_real_operations(document: dict[str, Any]) -> None:
    """The exclusions name paths that exist, so a rename cannot leave a stale exclusion that
    silently widens the hole. `POST /score` declares its own `429` (`RL-1347`)."""
    paths = document["paths"]
    assert f"{API_PREFIX}/auth/config" in paths
    assert "429" in paths[_SCORE_FAMILY]["post"]["responses"]
    assert "429" not in paths[f"{API_PREFIX}/auth/config"]["get"]["responses"]
