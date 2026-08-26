"""`require_identity` authenticates without resolving a workspace selection.

It exists for the one surface a principal must reach before it has a selection: the switch
endpoints in `me.py`. `require_caller` refuses a multi-membership principal with no header
(`WORKSPACE_SELECTION_REQUIRED`), which is exactly the state a first selection starts from.
"""

from __future__ import annotations

from typing import Annotated

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.api.deps import DEV_PRINCIPAL_HEADER, Caller, IdentityDep, require_caller
from app.auth.oidc import TokenClaims
from app.auth.service import authenticate_bearer
from app.db.models import WorkspaceMemberRow
from app.db.session import Database
from app.main import create_app
from app.platform import workspaces
from model_schema import new_uuid7

pytestmark = pytest.mark.req("FR-PLAT-63")

ISSUER = "https://idp.test.example/realms/gip"


class StubVerifier:
    """Returns fixed claims.

    Copied from `test_workspace_selection.py` rather than imported: neither it nor
    `_claims` is part of that module's surface, and a test module is not an import target
    for another one.
    """

    def __init__(self, claims: TokenClaims) -> None:
        self._claims = claims

    @property
    def issuer(self) -> str:
        return ISSUER

    def verify(self, token: str) -> TokenClaims:
        return self._claims


def _claims(subject: str) -> TokenClaims:
    return TokenClaims(
        subject=subject, email="a.actuary@insurer.example", name="A Actuary", groups=(), raw={}
    )


def _with_identity_route(app: FastAPI) -> TestClient:
    """The test app plus one throwaway route that echoes the identity dependency."""

    @app.get("/__test_identity", tags=["test"])
    async def echo_identity(identity: IdentityDep) -> dict[str, object]:
        return {
            "principal_id": str(identity.principal.id),
            "workspaces": sorted(str(w) for w in identity.workspaces),
        }

    return TestClient(app, raise_server_exceptions=False)


CallerDep = Annotated[Caller, Depends(require_caller)]


def _with_caller_route(app: FastAPI) -> TestClient:
    """The test app plus one throwaway route that echoes the resolved caller."""

    @app.get("/__test_caller", tags=["test"])
    async def echo_caller(caller: CallerDep) -> dict[str, object]:
        return {
            "principal_id": str(caller.principal.id),
            "workspace_id": str(caller.workspace_id),
        }

    return TestClient(app, raise_server_exceptions=False)


async def _membership(database: Database, user_id, workspace_id) -> None:
    """A membership naming a workspace that exists (FR-PLAT-62's foreign key)."""
    async with database.unit_of_work() as session:
        await workspaces.ensure_workspace(session, workspace_id=workspace_id)
        session.add(WorkspaceMemberRow(user_id=user_id, workspace_id=workspace_id))


async def test_a_multi_membership_principal_without_a_header_is_authenticated(
    database: Database, api_settings
) -> None:
    """A first selection starts from the very state `require_caller` refuses.

    The refusal belongs to the selection, not to auth: a principal that has not chosen
    yet must still be able to read the list it would choose from.
    """
    subject = f"user-{new_uuid7().hex[-12:]}"
    claims = _claims(subject)
    ids = []
    async with database.unit_of_work() as session:
        identity = await authenticate_bearer(session, StubVerifier(claims), "t")
        for _ in range(2):
            workspace_id = new_uuid7()
            # A membership names a workspace that exists (FR-PLAT-62's foreign key).
            await workspaces.ensure_workspace(session, workspace_id=workspace_id)
            session.add(
                WorkspaceMemberRow(
                    user_id=identity.principal.id, workspace_id=workspace_id
                )
            )
            ids.append(workspace_id)

    client = _with_identity_route(create_app(api_settings))
    client.app.state.oidc_verifier = StubVerifier(claims)
    with client:
        response = client.get(
            "/__test_identity", headers={"Authorization": "Bearer t"}
        )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["principal_id"] == str(identity.principal.id)
    assert body["workspaces"] == sorted(str(w) for w in ids)


def test_no_credential_with_dev_auth_disabled_is_unauthenticated(client: TestClient) -> None:
    """No credential falls through every branch to the dev gate, which is off."""
    response = _with_identity_route(client.app).get("/__test_identity")

    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHENTICATED"


async def test_dev_principal_workspace_is_checked_against_memberships(
    database: Database, api_settings
) -> None:
    """The dev caller resolves its workspace from `Workspace-Id`, like the bearer path.

    Before this task the request fails for a different reason — both dev headers were
    required — which is exactly the refusal this task removes.
    """
    principal_id = new_uuid7()
    first, second = new_uuid7(), new_uuid7()
    await _membership(database, principal_id, first)
    await _membership(database, principal_id, second)

    client = _with_caller_route(create_app(api_settings))
    with client:
        response = client.get(
            "/__test_caller",
            headers={
                DEV_PRINCIPAL_HEADER: str(principal_id),
                "Workspace-Id": str(second),
            },
        )

    assert response.status_code == 200, response.text
    assert response.json()["workspace_id"] == str(second)


async def test_dev_principal_with_several_memberships_and_no_header_is_refused(
    database: Database, api_settings
) -> None:
    """An unmade choice is refused for a dev principal exactly as for a bearer one."""
    principal_id = new_uuid7()
    await _membership(database, principal_id, new_uuid7())
    await _membership(database, principal_id, new_uuid7())

    client = _with_caller_route(create_app(api_settings))
    with client:
        response = client.get(
            "/__test_caller", headers={DEV_PRINCIPAL_HEADER: str(principal_id)}
        )

    assert response.status_code == 403
    assert response.json()["code"] == "WORKSPACE_SELECTION_REQUIRED"


async def test_dev_principal_naming_a_non_membership_is_denied(
    database: Database, api_settings
) -> None:
    """The choice is checked against the memberships, and the old pin is not honoured.

    The literal header name in the second half is deliberate: this task deletes
    `DEV_WORKSPACE_HEADER` from `deps.py`, and the request proves the pin is gone, not
    merely unused. Before this task the pin named the caller's workspace outright; now a
    leftover `x-dev-workspace-id` buys nothing — the workspace is the single
    membership's, never the pin's value.
    """
    principal_id = new_uuid7()
    member, outsider = new_uuid7(), new_uuid7()
    await _membership(database, principal_id, member)

    client = _with_caller_route(create_app(api_settings))
    with client:
        response = client.get(
            "/__test_caller",
            headers={
                DEV_PRINCIPAL_HEADER: str(principal_id),
                "Workspace-Id": str(outsider),
            },
        )
        assert response.status_code == 403
        assert response.json()["code"] == "WORKSPACE_SCOPE_DENIED"

        response = client.get(
            "/__test_caller",
            headers={
                DEV_PRINCIPAL_HEADER: str(principal_id),
                "x-dev-workspace-id": str(outsider),
            },
        )
        assert response.status_code == 200, response.text
        assert response.json()["workspace_id"] == str(member)
