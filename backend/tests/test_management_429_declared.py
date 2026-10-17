"""An `/api/v1` operation declares `429` if and only if it can return one (`RL-1687`; the lead's
ruling "2026-10-16 10:30:18 BST" and its amendment; WK-674 Slice 4).

The management limit and the scoring limit make routes return `429 RATE_LIMITED`; an undeclared
status is the drift `RL-1347` rule 4 closed for `/score`. One router-level mechanism declares it
(`app.main` `counted()`; `score.router` declares per route because it mixes three cases), and
this test walks the assembled OpenAPI document and holds the whole set.

`_CANNOT_429` is EXACTLY the operations that cannot return it, each with its reason. The second
test reads each route's dependency tree and fails if an excluded operation gains a counting
dependency, or if an operation outside the list has none, so the list cannot rot silently.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from typing import Any

import pytest
from fastapi.routing import APIRoute
from starlette.routing import BaseRoute

API_PREFIX = "/api/v1"
_METHODS = frozenset({"get", "put", "post", "delete", "options", "head", "patch", "trace"})

#: (method, path) -> why it cannot return 429.
_CANNOT_429: dict[tuple[str, str], str] = {
    ("get", f"{API_PREFIX}/auth/config"): "not authenticated: no Principal, so nothing to count",
    ("post", f"{API_PREFIX}/score/batch"): (
        "`requires(SCORE_BATCH, management_counted=False)` and no scoring limiter: it submits a "
        "Job and is counted by neither limit"
    ),
}


@pytest.fixture(scope="module")
def app() -> Any:
    from app.config import Environment, Settings
    from app.main import create_app

    return create_app(Settings(environment=Environment.LOCAL, version="test"))


def _operations(document: dict[str, Any]) -> list[tuple[str, str]]:
    return sorted(
        (method, path)
        for path, item in document["paths"].items()
        if path.startswith(f"{API_PREFIX}/")
        for method in item
        if method in _METHODS
    )


@pytest.mark.req("FR-452")
def test_every_operation_that_can_return_429_declares_it(app: Any) -> None:
    """Red when the router-level mechanism is removed from `app.main`: the first operation
    without a `429` response is named in the failure. An operation in `_CANNOT_429` must NOT
    declare it (an advertised error it never produces)."""
    document = app.openapi()
    operations = _operations(document)
    assert operations, "no /api/v1 operation was found: the walk is vacuous"
    missing = []
    advertised = []
    for method, path in operations:
        declares = "429" in document["paths"][path][method].get("responses", {})
        if (method, path) in _CANNOT_429:
            if declares:
                advertised.append(f"{method.upper()} {path}")
        elif not declares:
            missing.append(f"{method.upper()} {path}")
    assert not missing, (
        f"{len(missing)} of {len(operations)} operations do not declare 429; first: {missing[0]}"
    )
    assert not advertised, f"declares 429 but cannot return it: {advertised}"


def _flattened_operations(
    routes: Sequence[BaseRoute], prefix: str = ""
) -> Iterator[tuple[str, str, APIRoute]]:
    """Every `(METHOD, path, route)`, descending into included routers.

    FastAPI wraps `include_router` in an `_IncludedRouter` that holds the included router's routes
    as `original_router.routes` and the include's `prefix` in `include_context`, so `app.routes`
    alone shows none of the `/api/v1` operations (the same descent as
    `test_api_authorisation_sweep._flattened_operations`).
    """
    for route in routes:
        original = getattr(route, "original_router", None)
        if original is not None:
            yield from _flattened_operations(
                original.routes,
                prefix + route.include_context.prefix,  # type: ignore[attr-defined]
            )
        elif isinstance(route, APIRoute) and route.include_in_schema:
            for method in sorted(route.methods):
                yield method, prefix + route.path, route


def _calls(dependant: Any) -> list[Any]:
    found = []
    for sub in dependant.dependencies:
        found.append(sub.call)
        found.extend(_calls(sub))
    return found


def _counts(call: Any) -> bool:
    from app.api import authz, score

    if getattr(call, authz.MANAGEMENT_COUNTED_ATTRIBUTE, False):
        return True
    return call in (
        authz.counted_caller,
        authz.counted_identity,
        authz.management_counter,
        score._enforce_score_rate_limit,
    )


@pytest.mark.req("FR-452")
def test_the_cannot_429_list_matches_the_routes_dependencies(app: Any) -> None:
    """An excluded operation has no counting dependency; every other `/api/v1` operation has one.
    Red: an excluded route gains `requires()` / `counted_caller` / the scoring limiter (it can
    now 429 and must declare it), or a counted route loses its dependency (it should join the
    list)."""
    seen = set()
    for method, path, route in _flattened_operations(app.routes):
        if not path.startswith(f"{API_PREFIX}/"):
            continue
        counted = any(_counts(call) for call in _calls(route.dependant))
        key = (method.lower(), path)
        seen.add(key)
        if key in _CANNOT_429:
            assert not counted, f"{method} {path} is excluded but now counts"
        else:
            assert counted, f"{method} {path} has no counting dependency: exclude it?"
    assert set(_CANNOT_429) <= seen, f"stale exclusions: {sorted(set(_CANNOT_429) - seen)}"
