"""Every published operation refuses an anonymous caller and a role-less one (FR-343).

`00` §5.1 makes authorisation per-route: each handler declares
`Annotated[Caller, Depends(requires(Perm.X))]`. A route that omits it, or downgrades it to
plain authentication, is a hole no other test would see — the suite named three paths out
of fifty-nine, and an injection that replaced `requires(Perm.DATASET_READ)` with
`require_caller` on the reference routes left all 609 tests green.

The sweep is derived from `app.openapi()`, so a route added tomorrow is covered on the day
it is added rather than when somebody remembers.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Any

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from starlette.routing import BaseRoute

from app.api.deps import DEV_PRINCIPAL_HEADER
from model_schema import new_uuid7

#: Operational surfaces, deliberately open. `07` §5.1 publishes them for probes and
#: scrapers that hold no identity: a liveness check that needed a credential could not run
#: before authentication was working, which is when it matters most.
#:
#: `07` §5.1 also publishes the OIDC bootstrap values unauthenticated (FR-394): the
#: browser cannot start the login it needs a credential for without first learning the
#: issuer and `client_id` — the endpoint is the channel, not a second identity.
OPEN_BY_DESIGN = {
    "/healthz",
    "/readyz",
    "/version",
    "/metrics",
    "/openapi.json",
    "/docs",
    "/api/v1/auth/config",
}

#: Authenticated, but permission-free **on purpose**, each with the reason.
#:
#: An exclusion nobody states is how a hole gets parked in a set literal, so every entry
#: here carries one and `test_the_permission_free_routes_really_are_permission_free`
#: checks the claim.
NO_PERMISSION_REQUIRED = {
    # "Who am I and what may I do" — a caller with no roles must be able to ask, and the
    # answer is the empty permission set.
    "/api/v1/me",
    # FR-396's second amendment (PR #237): the list a first selection is made from is
    # deliberately unscoped — a principal that needs to choose has no selection yet, so no
    # workspace exists to hold a role check. A role is always role-in-a-workspace.
    "/api/v1/me/workspaces",
    # Facts about the repository, no workspace data, and only where development identity
    # exists at all (FR-408).
    "/api/v1/demo/guide",
    # `06`'s deliberate choice, stated at `app/api/approvals.py`: submitting is *asking*,
    # and the module owning the artifact already decided whether this principal could
    # create it. Reading the queue and the policy follow the same rule.
    #
    # **`06` does not say so.** The rationale is in a handler docstring for one of the
    # three and nowhere for the other two — raised for the spec rather than settled here.
    "/api/v1/approval-requests",
    "/api/v1/approval-requests/{request_id}",
    "/api/v1/approval-policy",
}

#: Routes whose permission is checked **in the handler**, not by `requires()`: each names the
#: code site (path under `backend/src/app`, line, and the text that must be on that line), so
#: the list cannot rot silently — `test_the_handler_guarded_routes_still_check_at_their_site`
#: reads each site. Static analysis treats a route listed here as guarded; nothing else is
#: skipped (A1, WK-674 S2; the maintainer's 2026-09-30 11:01:50 BST entry, item (e)).
#:
#: * `POST /api/v1/validation-rules`: `01` §4.5's Admin-or-author rule picks the permission
#:   after reading the rule body (OQ-559), so the check is in the platform function.
#: * `POST /api/v1/me/workspace`: **no permission is needed** — "who am I and where may I
#:   work" has no workspace to hold a role check. The refusals are the membership checks of
#:   `00` FR-396 and FR-397 (a malformed `Workspace-Id`, the workspace entered, the workspace
#:   left), each raising `WORKSPACE_SCOPE_DENIED`.
HANDLER_GUARDED: dict[tuple[str, str], tuple[tuple[str, int, str], ...]] = {
    ("POST", "/api/v1/validation-rules"): (
        ("platform/validation_rules.py", 212, "require_permission("),
        ("platform/validation_rules.py", 219, "require_permission("),
    ),
    ("POST", "/api/v1/me/workspace"): (
        ("api/me.py", 241, "WORKSPACE_SCOPE_DENIED"),
        ("api/me.py", 251, "WORKSPACE_SCOPE_DENIED"),
        ("api/me.py", 260, "WORKSPACE_SCOPE_DENIED"),
    ),
    # `deployment:promote` with the Environment as the resource (`RL-1301` B.2): the Environment
    # row the resource names is loaded in the handler, so neither route carries a bare
    # `requires(...)`. Both reach the one check in `_authorised_environment` (WK-674 Slice 2,
    # PL-1392 Task 5).
    ("POST", "/api/v1/environments/{env}/deployments"): (
        ("platform/deployments.py", 84, "require_permission("),
    ),
    ("POST", "/api/v1/environments/{env}/deployment-requests"): (
        ("platform/deployments.py", 84, "require_permission("),
    ),
}

_METHODS = ("get", "post", "put", "patch", "delete")


def _flattened_operations(
    routes: Sequence[BaseRoute], prefix: str = ""
) -> Iterator[tuple[str, str, APIRoute]]:
    """Every `(METHOD, path, route)`, descending into included routers (A1, WK-674 S2).

    FastAPI 0.141.1 wraps `include_router` in an `_IncludedRouter` that holds the included
    router's own routes as `original_router.routes` and the include's `prefix` in
    `include_context`. `app.routes` is therefore two plain routes and twenty-three wrappers,
    and a loop over `app.routes` that tests `isinstance(route, APIRoute)` sees only the two:
    the sweep's static half was vacuous over the whole `/api/v1` surface.
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


def _declares_a_permission(route: APIRoute) -> bool:
    from app.api.authz import PERMISSION_ATTRIBUTE

    return any(
        getattr(dependency.call, PERMISSION_ATTRIBUTE, None) is not None
        for dependency in route.dependant.dependencies
    )


def _unguarded_operations(client: TestClient) -> list[str]:
    unguarded: list[str] = []
    for method, path, route in _flattened_operations(client.app.routes):
        if path in OPEN_BY_DESIGN or path in NO_PERMISSION_REQUIRED:
            continue
        if (method, path) in HANDLER_GUARDED or _declares_a_permission(route):
            continue
        unguarded.append(f"{method} {path}")
    return unguarded


def _published_operations(client: TestClient) -> set[tuple[str, str]]:
    return {
        (method.upper(), path)
        for path, operations in client.app.openapi()["paths"].items()
        for method in operations
        if method in _METHODS
    }


def _operations(client: TestClient) -> list[tuple[str, str]]:
    document = client.app.openapi()
    return sorted(
        (method.upper(), path)
        for path, operations in document["paths"].items()
        for method in operations
        if method in _METHODS and path not in OPEN_BY_DESIGN
    )


def _concrete(path: str) -> str:
    """Fill path parameters with values that exist nowhere.

    The refusal must precede the lookup: a 404 for a caller who should have been refused
    would tell them the id does not exist, which is itself an answer they had no right to.
    """
    filled = path
    while "{" in filled:
        head, _, rest = filled.partition("{")
        _, _, tail = rest.partition("}")
        filled = f"{head}{new_uuid7()}{tail}"
    return filled


#: The three patterns the contract uses where the schema carries no `examples`: the slug
#: grammar (`_SLUG`, `refs.py`), a SHA-256 digest and a peril code. A fourth is a decision,
#: not a default.
_PATTERN_VALUES: dict[str, str] = {
    "^[a-z0-9][a-z0-9-]{1,62}$": "sweep-slug",
    "^[0-9a-f]{64}$": "0" * 64,
    "^[A-Z][A-Z0-9_]{0,31}$": "SWEEP",  # a peril code
    # `DecimalStr` (model_schema.money): `DislocationSpec`'s band edges and mover threshold, a
    # fourth pattern ruled added by the maintainer's 2026-10-10 02:43:18 entry (WK-673 Slice 4).
    "^-?[0-9]+(\\.[0-9]+)?$": "1",
}


class _UnsatisfiableError(Exception):
    """The builder could not produce a value the schema accepts."""


def _resolve(schema: dict[str, Any], document: dict[str, Any]) -> dict[str, Any]:
    while "$ref" in schema:
        node: Any = document
        for part in schema["$ref"].removeprefix("#/").split("/"):
            node = node[part]
        schema = node
    return schema


def _value(schema: dict[str, Any], document: dict[str, Any], depth: int = 0) -> Any:
    """A value the schema accepts, from its own declarations (required properties only).

    Not a general generator: it covers what this contract uses — `$ref`, enums and
    constants, `format` (`uuid`, `date`, `date-time`), `anyOf`/`oneOf` (the first branch it
    can satisfy), `allOf` (merged), a string `pattern` only through `examples`, strings of
    `minLength`, numbers at `minimum`. Anything else raises `_UnsatisfiableError`.
    """
    if depth > 8:
        raise _UnsatisfiableError("schema nests deeper than 8")
    schema = _resolve(schema, document)
    if "const" in schema:
        return schema["const"]
    if schema.get("examples"):
        return schema["examples"][0]
    if "enum" in schema:
        return schema["enum"][0]
    if "allOf" in schema:
        merged: dict[str, Any] = {}
        for branch in schema["allOf"]:
            part = _value(branch, document, depth + 1)
            if not isinstance(part, dict):
                return part
            merged.update(part)
        return merged
    for key in ("anyOf", "oneOf"):
        if key in schema:
            for branch in schema[key]:
                if _resolve(branch, document).get("type") == "null":
                    continue
                try:
                    return _value(branch, document, depth + 1)
                except _UnsatisfiableError:
                    continue
            raise _UnsatisfiableError(f"no {key} branch is satisfiable")
    kind = schema.get("type")
    if isinstance(kind, list):
        kind = next((item for item in kind if item != "null"), "null")
    if kind == "object" or "properties" in schema:
        properties = schema.get("properties", {})
        return {
            name: _value(properties[name], document, depth + 1)
            for name in schema.get("required", [])
        }
    if kind == "array":
        return [_value(schema["items"], document, depth + 1)] * schema.get("minItems", 0)
    if kind == "string":
        match schema.get("format"):
            case "uuid":
                return str(new_uuid7())
            case "date":
                return "2026-01-01"
            case "date-time":
                return "2026-01-01T00:00:00Z"
            case "binary":
                raise _UnsatisfiableError("a file part")
        if "pattern" in schema:
            if schema["pattern"] in _PATTERN_VALUES:
                return _PATTERN_VALUES[schema["pattern"]]
            raise _UnsatisfiableError(f"pattern {schema['pattern']!r} with no example")
        return "x" * max(1, schema.get("minLength", 0))
    if kind in {"integer", "number"}:
        return schema.get(
            "minimum", schema.get("exclusiveMinimum", 0) + 1 if "exclusiveMinimum" in schema else 1
        )
    if kind == "boolean":
        return True
    if kind == "null":
        return None
    raise _UnsatisfiableError(f"no builder for {schema!r}")


#: Operations whose request the builder cannot satisfy, each with the reason. Its size is
#: asserted, so it cannot grow silently: a new entry is a decision, not a convenience.
UNSATISFIABLE: dict[tuple[str, str], str] = {
    ("POST", "/api/v1/rate-tables/{slug}@{version}/import"): "multipart/form-data with a file part",
    ("POST", "/api/v1/sources/{source_id}/preview"): "multipart/form-data with a file part",
}


#: Routes whose permission is checked against a **resource the handler loads**, so a request
#: that names no real resource is refused for that, not for the permission. Each maps the path
#: parameter to a real value and a body field to one the handler's own first check accepts
#: (WK-674 Slice 2, PL-1392 Task 5: the Environment is the resource of `deployment:promote`,
#: `RL-1301` B.2, and G3 refuses a non-Rating-Version reference before any row is read).
RESOURCE_BACKED: dict[tuple[str, str], tuple[dict[str, str], dict[str, Any]]] = {
    ("POST", "/api/v1/environments/{env}/deployments"): (
        {"env": "dev"},
        {"rating_version_ref": "rating_version:sweep-version@1"},
    ),
    ("POST", "/api/v1/environments/{env}/deployment-requests"): (
        {"env": "dev"},
        {"rating_version_ref": "rating_version:sweep-version@1"},
    ),
}


def _request_for(
    document: dict[str, Any], method: str, path: str
) -> tuple[str, dict[str, Any], dict[str, Any] | None]:
    """The concrete path, the query parameters and the JSON body of a valid request."""
    filled, query, body = _built_request(document, method, path)
    backed = RESOURCE_BACKED.get((method, path))
    if backed is not None:
        values, patch = backed
        filled = path
        for name, value in values.items():
            filled = filled.replace("{" + name + "}", value)
        assert body is not None
        body = {**body, **patch}
    return filled, query, body


def _built_request(
    document: dict[str, Any], method: str, path: str
) -> tuple[str, dict[str, Any], dict[str, Any] | None]:
    operation = document["paths"][path][method.lower()]
    filled = path
    query: dict[str, Any] = {}
    for parameter in operation.get("parameters", []):
        if parameter["in"] not in {"path", "query"} or not (
            parameter["in"] == "path" or parameter.get("required")
        ):
            continue
        value = _value(parameter["schema"], document)
        if parameter["in"] == "path":
            filled = filled.replace("{" + parameter["name"] + "}", str(value))
        else:
            query[parameter["name"]] = value
    body = None
    content = operation.get("requestBody", {}).get("content", {})
    if "application/json" in content:
        body = _value(content["application/json"]["schema"], document)
    elif content:
        raise _UnsatisfiableError(f"request body of {sorted(content)}")
    return filled, query, body


@pytest.mark.req("FR-343")
def test_every_operation_refuses_an_anonymous_caller(api_client: TestClient) -> None:
    unauthenticated: list[str] = []
    for method, path in _operations(api_client):
        response = api_client.request(method, _concrete(path), json={})
        if response.status_code != 401:
            unauthenticated.append(f"{method} {path} → {response.status_code}")
    assert not unauthenticated, "reachable without a credential:\n" + "\n".join(unauthenticated)


@pytest.mark.req("FR-343")
async def test_every_operation_refuses_a_caller_holding_no_roles(
    api_client: TestClient, membership, workspace_id
) -> None:
    """A principal with no grants is authenticated and entitled to nothing (FR-390).

    `403`, not `404` and not `422`: the permission check must resolve before the handler
    touches an id or a body, or the refusal leaks whether the id exists.

    The caller holds a membership but no role (W6b-11). A caller with no membership at
    all is refused earlier, with `UNAUTHENTICATED` — the wrong refusal to pin here, since
    it proves nothing about the per-route permission declarations this test guards. The
    code is asserted, not just the status: the refusal must come from the role check,
    never from the membership check.
    """
    caller = new_uuid7()
    await membership(principal_id=caller)
    headers = {
        DEV_PRINCIPAL_HEADER: str(caller),
        "Workspace-Id": str(workspace_id),
    }
    document = api_client.app.openapi()
    permitted: list[str] = []
    wrong_refusal: list[str] = []
    skipped: dict[tuple[str, str], str] = {}
    for method, path in _operations(api_client):
        if path in NO_PERMISSION_REQUIRED:
            continue
        try:
            filled, query, body = _request_for(document, method, path)
        except _UnsatisfiableError as exc:
            skipped[(method, path)] = str(exc)
            continue
        # A valid body for every route: a 422 is not a refusal (A1 (d)), it only proves the
        # body was malformed. Exactly 403, from the permission or the membership check.
        response = api_client.request(method, filled, params=query, headers=headers, json=body)
        if response.status_code != 403:
            permitted.append(f"{method} {path} → {response.status_code}")
            continue
        code = response.json().get("code")
        allowed = (
            {"PERMISSION_DENIED", "WORKSPACE_SCOPE_DENIED"}
            if (method, path) in HANDLER_GUARDED
            else {"PERMISSION_DENIED"}
        )
        if code not in allowed:
            wrong_refusal.append(f"{method} {path} → {code}")
    assert not permitted, "reachable with no roles:\n" + "\n".join(permitted)
    assert not wrong_refusal, "refused for the wrong reason:\n" + "\n".join(wrong_refusal)
    assert len(UNSATISFIABLE) == 2, (
        "UNSATISFIABLE grew: each entry is a decision, not a convenience"
    )
    assert set(skipped) == set(UNSATISFIABLE), (
        f"the builder skipped {sorted(skipped.items())}; "
        f"UNSATISFIABLE names {sorted(UNSATISFIABLE)}"
    )


@pytest.mark.req("FR-343")
async def test_the_permission_free_routes_really_are_permission_free(
    api_client: TestClient, membership, workspace_id
) -> None:
    """The negative of the exclusion list: it must name routes that behave as claimed.

    An exclusion nobody checks is how a hole gets parked in a set literal.

    The caller holds a membership but no role, exactly like the refusal sweep: these
    routes must answer a caller the permission checks would refuse everywhere else.
    """
    caller = new_uuid7()
    await membership(principal_id=caller)
    headers = {
        DEV_PRINCIPAL_HEADER: str(caller),
        "Workspace-Id": str(workspace_id),
    }
    for path in sorted(NO_PERMISSION_REQUIRED):
        response = api_client.get(_concrete(path), headers=headers)
        # Not 403: these routes are excluded from the sweep *because* they answer a
        # role-less caller. 404 is an answer — the id in the path does not exist.
        assert response.status_code in {200, 404}, f"{path} → {response.status_code}"
    # ...and every one of them still requires a credential.
    for path in sorted(NO_PERMISSION_REQUIRED):
        assert api_client.get(_concrete(path)).status_code == 401, path


@pytest.mark.req("FR-343")
def test_every_operation_declares_the_permission_it_enforces(api_client: TestClient) -> None:
    """The static half, and the stronger one.

    A response sweep cannot distinguish "refused for want of a permission" from "refused
    for a malformed body": `POST` with `{}` answers 422 either way, so a route enforcing
    nothing would pass it. This asks each route which permission it declares — which is
    what an injection replacing `requires(Perm.DATASET_READ)` with `require_caller`
    actually changes.
    """
    unguarded = _unguarded_operations(api_client)
    assert not unguarded, "no permission declared:\n" + "\n".join(unguarded)


@pytest.mark.req("FR-343")
def test_a_guard_removed_from_a_real_route_is_seen(
    api_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Broken input for the static sweep: it must fail when a route loses `requires()`.

    The route is a real one reached only through an included router, so a sweep that does
    not descend into them cannot see the removal (A1). `monkeypatch` restores it.
    """
    from app.api.authz import PERMISSION_ATTRIBUTE

    target = ("GET", "/api/v1/datasets")
    route = next(
        route
        for method, path, route in _flattened_operations(api_client.app.routes)
        if (method, path) == target
    )
    assert _declares_a_permission(route)
    kept = [
        dependency
        for dependency in route.dependant.dependencies
        if getattr(dependency.call, PERMISSION_ATTRIBUTE, None) is None
    ]
    monkeypatch.setattr(route.dependant, "dependencies", kept)
    assert _unguarded_operations(api_client) == [f"{target[0]} {target[1]}"]


@pytest.mark.req("FR-343")
def test_the_handler_guarded_routes_still_check_at_their_site(api_client: TestClient) -> None:
    """An allow-list entry is a claim about a line of code; read the line."""
    app_root = Path(__file__).resolve().parents[1] / "src" / "app"
    published = _published_operations(api_client)
    for (method, path), sites in HANDLER_GUARDED.items():
        assert (method, path) in published, f"{method} {path} is no longer a published operation"
        for file, line, needle in sites:
            text = (app_root / file).read_text().splitlines()[line - 1]
            assert needle in text, (
                f"{method} {path}: {file}:{line} no longer holds {needle!r}: {text!r}"
            )


@pytest.mark.req("FR-343")
def test_every_operation_is_accounted_for_by_exactly_one_class(api_client: TestClient) -> None:
    """The four classes partition the published operations (Acceptance 12 (g))."""
    classes: dict[str, set[tuple[str, str]]] = {
        "open by design": set(),
        "permission-free on purpose": set(),
        "handler-guarded": set(),
        "declared by requires()": set(),
    }
    unaccounted: list[str] = []
    for method, path, route in _flattened_operations(api_client.app.routes):
        if path in OPEN_BY_DESIGN:
            classes["open by design"].add((method, path))
        elif path in NO_PERMISSION_REQUIRED:
            classes["permission-free on purpose"].add((method, path))
        elif (method, path) in HANDLER_GUARDED:
            classes["handler-guarded"].add((method, path))
        elif _declares_a_permission(route):
            classes["declared by requires()"].add((method, path))
        else:
            unaccounted.append(f"{method} {path}")
    assert not unaccounted, "in no class:\n" + "\n".join(unaccounted)
    published = _published_operations(api_client)
    assert sum(len(members) for members in classes.values()) == len(published)
    assert set().union(*classes.values()) == published
    names = list(classes)
    for index, first in enumerate(names):
        for second in names[index + 1 :]:
            overlap = classes[first] & classes[second]
            assert not overlap, f"{first} and {second} both claim {sorted(overlap)}"


@pytest.mark.req("FR-343")
def test_the_sweep_covers_the_whole_published_surface(api_client: TestClient) -> None:
    """A sweep that silently enumerated nothing would pass every assertion above."""
    operations = _operations(api_client)
    assert len(operations) >= 50, f"only {len(operations)} operations enumerated"
    paths = {path for _, path in operations}
    for expected in ("/api/v1/datasets", "/api/v1/reference-tables", "/api/v1/jobs"):
        assert expected in paths


@pytest.mark.req("FR-343")
def test_the_static_sweep_iterates_every_published_operation(api_client: TestClient) -> None:
    iterated = {(method, path) for method, path, _ in _flattened_operations(api_client.app.routes)}
    published = _published_operations(api_client)
    assert len(iterated) == len(published), (
        f"the static sweep iterated {len(iterated)} operations; "
        f"the contract publishes {len(published)}"
    )
    assert iterated == published, sorted(iterated ^ published)
