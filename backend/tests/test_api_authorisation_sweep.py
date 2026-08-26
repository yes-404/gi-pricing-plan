"""Every published operation refuses an anonymous caller and a role-less one (FR-GOV-2).

`00` §5.1 makes authorisation per-route: each handler declares
`Annotated[Caller, Depends(requires(Perm.X))]`. A route that omits it, or downgrades it to
plain authentication, is a hole no other test would see — the suite named three paths out
of fifty-nine, and an injection that replaced `requires(Perm.DATASET_READ)` with
`require_caller` on the reference routes left all 609 tests green.

The sweep is derived from `app.openapi()`, so a route added tomorrow is covered on the day
it is added rather than when somebody remembers.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.deps import DEV_PRINCIPAL_HEADER
from model_schema import new_uuid7

#: Operational surfaces, deliberately open. `07` §5.1 publishes them for probes and
#: scrapers that hold no identity: a liveness check that needed a credential could not run
#: before authentication was working, which is when it matters most.
#:
#: `07` §5.1 also publishes the OIDC bootstrap values unauthenticated (FR-PLAT-66): the
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
    # FR-PLAT-63's second amendment (PR #237): the list a first selection is made from is
    # deliberately unscoped — a principal that needs to choose has no selection yet, so no
    # workspace exists to hold a role check. A role is always role-in-a-workspace.
    "/api/v1/me/workspaces",
    # Facts about the repository, no workspace data, and only where development identity
    # exists at all (FR-PLAT-53).
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

_METHODS = ("get", "post", "put", "patch", "delete")


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


@pytest.mark.req("FR-GOV-2")
def test_every_operation_refuses_an_anonymous_caller(api_client: TestClient) -> None:
    unauthenticated: list[str] = []
    for method, path in _operations(api_client):
        response = api_client.request(method, _concrete(path), json={})
        if response.status_code != 401:
            unauthenticated.append(f"{method} {path} → {response.status_code}")
    assert not unauthenticated, "reachable without a credential:\n" + "\n".join(unauthenticated)


@pytest.mark.req("FR-GOV-2")
async def test_every_operation_refuses_a_caller_holding_no_roles(
    api_client: TestClient, membership, workspace_id
) -> None:
    """A principal with no grants is authenticated and entitled to nothing (FR-PLAT-4).

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
    permitted: list[str] = []
    wrong_refusal: list[str] = []
    for method, path in _operations(api_client):
        if path in NO_PERMISSION_REQUIRED:
            continue
        response = api_client.request(method, _concrete(path), headers=headers, json={})
        # 422 counts as refused for a body-carrying method: FastAPI validates the body
        # alongside the dependencies, so an empty body can answer before the permission
        # does. Nothing is disclosed — the schema is in the published contract — and the
        # question "does this route enforce anything at all" is answered statically by
        # `test_every_operation_declares_the_permission_it_enforces`, which an empty body
        # cannot fool.
        refused = {403, 422} if method in {"POST", "PUT", "PATCH"} else {403}
        if response.status_code not in refused:
            permitted.append(f"{method} {path} → {response.status_code}")
            continue
        if response.status_code == 403:
            code = response.json().get("code")
            if code != "PERMISSION_DENIED":
                wrong_refusal.append(f"{method} {path} → {code}")
    assert not permitted, "reachable with no roles:\n" + "\n".join(permitted)
    assert not wrong_refusal, "refused for the wrong reason:\n" + "\n".join(wrong_refusal)


@pytest.mark.req("FR-GOV-2")
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


@pytest.mark.req("FR-GOV-2")
def test_every_operation_declares_the_permission_it_enforces(api_client: TestClient) -> None:
    """The static half, and the stronger one.

    A response sweep cannot distinguish "refused for want of a permission" from "refused
    for a malformed body": `POST` with `{}` answers 422 either way, so a route enforcing
    nothing would pass it. This asks each route which permission it declares — which is
    what an injection replacing `requires(Perm.DATASET_READ)` with `require_caller`
    actually changes.
    """
    from fastapi.routing import APIRoute

    from app.api.authz import PERMISSION_ATTRIBUTE

    unguarded: list[str] = []
    for route in api_client.app.routes:
        if not isinstance(route, APIRoute) or route.path in OPEN_BY_DESIGN:
            continue
        if route.path in NO_PERMISSION_REQUIRED:
            continue
        declared = [
            dependency.call
            for dependency in route.dependant.dependencies
            if getattr(dependency.call, PERMISSION_ATTRIBUTE, None) is not None
        ]
        if not declared:
            unguarded.append(f"{sorted(route.methods)} {route.path}")
    assert not unguarded, "no permission declared:\n" + "\n".join(unguarded)


@pytest.mark.req("FR-GOV-2")
def test_the_sweep_covers_the_whole_published_surface(api_client: TestClient) -> None:
    """A sweep that silently enumerated nothing would pass every assertion above."""
    operations = _operations(api_client)
    assert len(operations) >= 50, f"only {len(operations)} operations enumerated"
    paths = {path for _, path in operations}
    for expected in ("/api/v1/datasets", "/api/v1/reference-tables", "/api/v1/jobs"):
        assert expected in paths
