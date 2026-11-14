"""Every 2xx response's media types in the generated OpenAPI are the route's declared wire types
(FD-1795, the FD-1684 sweep).

FD-1684's sweep predicate selected a 2xx media type only when its schema was the empty object, so
a route that answered `text/csv` but published `application/json` with a typed schema tripped
nothing. This compares, for every route and every 2xx status the document publishes, the media
types published with the ones the route declares:

- the media type of the route's `response_class` (`application/json` by default; none for the
  bare `Response` and `StreamingResponse`, which publish no content of their own), on the route's
  own status code, and a status that carries no body (1xx, 204, 304) publishes none;
- plus every media type the route names in `responses[<status>]["content"]`, which is how a
  route with a non-JSON body declares it, and, for a `responses` entry carrying a `model`, the
  class's media type (JSON when it has none), which is where FastAPI publishes that model.

It reads the document `create_app` generates and edits nothing under `docs/contracts/openapi/`.
"""

from __future__ import annotations

import copy
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute, iter_route_contexts

from app.config import Environment, Settings
from app.main import create_app

_HTTP_METHODS = frozenset({"get", "put", "post", "delete", "options", "head", "patch", "trace"})
_NO_BODY = frozenset({204, 304})


@pytest.fixture(scope="module")
def app() -> FastAPI:
    return create_app(Settings(environment=Environment.LOCAL, version="test"))


def _route_media_types(route: Any, status: str) -> set[str]:
    """The media types `route` declares for the 2xx `status`."""
    response_class: Any = route.response_class
    response_class = getattr(response_class, "value", response_class)  # a default placeholder
    declared: set[str] = set()
    for key, response in route.responses.items():
        if str(key) == status:
            declared |= set(response.get("content", {}))
            if "model" in response:  # published in the class's media type, JSON when it has none
                declared.add(response_class.media_type or "application/json")
    # An unset status code is the response class's own default, 200 for every class that
    # reaches a 2xx here (FastAPI reads it from the class's constructor).
    own_status = 200 if route.status_code is None else route.status_code
    if (
        status == str(own_status)
        and own_status not in _NO_BODY
        and response_class.media_type is not None
    ):
        declared.add(response_class.media_type)
    return declared


def _mismatches(app: FastAPI, document: dict[str, Any]) -> list[str]:
    """`METHOD path status: published {...}, declared {...}` for each 2xx response whose published
    media types differ from the route's declared ones."""
    # `include_router` nests routers, so the effective path, methods, responses and response
    # class of a route are read from FastAPI's own route contexts, the ones it builds the
    # document from.
    routes = {
        (method.lower(), route.path_format): route
        for route in iter_route_contexts(app.routes)
        if isinstance(route.original_route, APIRoute) and route.include_in_schema
        for method in route.methods
    }
    out: list[str] = []
    for path, item in document["paths"].items():
        for method, operation in item.items():
            if method not in _HTTP_METHODS:
                continue
            route = routes[(method, path)]
            for status, response in operation["responses"].items():
                if not status.startswith("2"):
                    continue
                published = set(response.get("content", {}))
                declared = _route_media_types(route, status)
                if published != declared:
                    out.append(
                        f"{method.upper()} {path} {status}: published {sorted(published)}, "
                        f"declared {sorted(declared)}"
                    )
    return out


@pytest.mark.req("FR-451")
def test_every_2xx_media_type_is_the_routes_declared_wire_type(app: FastAPI) -> None:
    assert _mismatches(app, app.openapi()) == []


@pytest.mark.req("FR-451")
def test_a_typed_json_schema_on_a_non_json_route_is_named_by_route(app: FastAPI) -> None:
    """The case the empty-schema predicate missed: `GET /api/v1/audit/export` answers CSV or
    JSON Lines; plant `application/json` with a typed schema in its place."""
    document = copy.deepcopy(app.openapi())
    export = document["paths"]["/api/v1/audit/export"]["get"]["responses"]["200"]
    assert set(export["content"]) == {"text/csv", "application/x-ndjson"}, "control"
    export["content"] = {"application/json": {"schema": {"type": "string"}}}
    found = _mismatches(app, document)
    assert len(found) == 1
    assert found[0].startswith("GET /api/v1/audit/export 200:")
    assert "application/json" in found[0]
