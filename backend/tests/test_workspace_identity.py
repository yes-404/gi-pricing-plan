"""`require_identity` authenticates without resolving a workspace selection.

It exists for the one surface a principal must reach before it has a selection: the switch
endpoints in `me.py`. `require_caller` refuses a multi-membership principal with no header
(`WORKSPACE_SELECTION_REQUIRED`), which is exactly the state a first selection starts from.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

import pytest

from app.api.deps import IdentityDep
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
