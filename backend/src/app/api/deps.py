"""Request dependencies: who is calling, and on whose behalf (FR-PLAT-1..4).

Three credential paths, tried in order, and every one of them can only *fail closed*:

1. `Authorization: Bearer <jwt>` — an OIDC access token, verified against the provider.
2. `Authorization: ApiKey <key>` / `X-API-Key` — a Service Account key.
3. Development headers — **local only**, and `Settings.require_startable` refuses to boot
   with them enabled in `uat` or `prod`.

With none of these configured or presented, the answer is `401`, never a default identity.

The workspace is not taken from the request. A caller states nothing about which tenant it
is acting in; the platform derives it from membership (users) or from the account's own
workspace (service accounts). A header-supplied workspace would make tenancy a claim rather
than a fact.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends, Request

from app.auth.oidc import OidcVerifier
from app.auth.service import AuthenticatedIdentity, authenticate_api_key, authenticate_bearer
from app.config import Settings
from app.db.session import Database
from app.errors import PlatformError
from model_schema import ActorKind, Principal

__all__ = ["Caller", "require_caller"]

#: Development-only headers. Named so they cannot be mistaken for a supported mechanism.
DEV_PRINCIPAL_HEADER = "x-dev-principal-id"
DEV_WORKSPACE_HEADER = "x-dev-workspace-id"


@dataclass(frozen=True)
class Caller:
    """The authenticated principal and the workspace it is acting in (FR-OVR-13)."""

    principal: Principal
    workspace_id: UUID
    environments: frozenset[str] = frozenset()
    permissions: frozenset[str] = frozenset()


def _settings(request: Request) -> Settings:
    settings: Settings = request.app.state.settings
    return settings


SettingsDep = Annotated[Settings, Depends(_settings)]


async def require_caller(request: Request, settings: SettingsDep) -> Caller:
    """Resolve the caller, or refuse."""
    authorization = request.headers.get("authorization", "")
    scheme, _, credential = authorization.partition(" ")
    scheme = scheme.lower()

    database: Database = request.app.state.database

    if scheme == "bearer" and credential:
        verifier: OidcVerifier = request.app.state.oidc_verifier
        async with database.unit_of_work() as session:
            identity = await authenticate_bearer(session, verifier, credential)
        return _single_workspace(identity)

    api_key = credential if scheme == "apikey" else request.headers.get("x-api-key")
    if api_key:
        async with database.unit_of_work() as session:
            identity = await authenticate_api_key(session, api_key)
        return _single_workspace(identity)

    return _development_caller(request, settings)


def _single_workspace(identity: AuthenticatedIdentity) -> Caller:
    """Collapse an authenticated identity to the one workspace it is acting in.

    A user may belong to several. Until the API carries a workspace selector — which
    arrives with governance in W3, alongside the roles that make the choice meaningful —
    a caller with more than one must choose, and the platform must not choose for them.
    """
    from app.auth.service import AuthenticatedIdentity

    assert isinstance(identity, AuthenticatedIdentity)
    if not identity.workspaces:
        raise PlatformError(
            "UNAUTHENTICATED",
            "No workspace access",
            403,
            "This principal is authenticated but is a member of no workspace. Access is "
            "granted explicitly (FR-PLAT-4); it is never the default.",
        )
    if len(identity.workspaces) > 1:
        raise PlatformError(
            "UNAUTHENTICATED",
            "Workspace selection required",
            403,
            "This principal belongs to more than one workspace and the API has no "
            "selector yet. Workspace selection arrives with W3.",
        )
    return Caller(
        principal=identity.principal,
        workspace_id=next(iter(identity.workspaces)),
        environments=identity.environments,
        permissions=identity.permissions,
    )


def _development_caller(request: Request, settings: Settings) -> Caller:
    """Local-only identity from headers. Refused outside `local`/`dev` at startup."""
    if not settings.dev_auth_enabled:
        raise PlatformError(
            "UNAUTHENTICATED",
            "Authentication required",
            401,
            "No credential was presented. Use an OIDC bearer token or a service account "
            "API key.",
        )

    principal_id = request.headers.get(DEV_PRINCIPAL_HEADER)
    workspace_id = request.headers.get(DEV_WORKSPACE_HEADER)
    if not principal_id or not workspace_id:
        raise PlatformError(
            "UNAUTHENTICATED",
            "Authentication required",
            401,
            f"Development identity is enabled; supply {DEV_PRINCIPAL_HEADER} and "
            f"{DEV_WORKSPACE_HEADER}.",
        )

    try:
        principal = Principal(
            kind=ActorKind.USER, id=UUID(principal_id), display="dev@localhost"
        )
        workspace = UUID(workspace_id)
    except ValueError as exc:
        raise PlatformError(
            "UNAUTHENTICATED",
            "Authentication required",
            401,
            "Development identity headers must be UUIDs.",
        ) from exc

    return Caller(principal=principal, workspace_id=workspace)


def job_identity(caller: Caller) -> dict[str, Any]:
    """Who asked, and in which workspace — carried in every domain Job's parameters.

    A handler receives only `row.parameters`, so without this it cannot attribute what it
    does, and every audit event a dataset job writes would read as "the system". That
    answers the wrong question: nobody asks whether the platform ingested a file.

    The workspace is included for the same reason and taken from the *caller*, never from
    the request body — a body-supplied workspace makes tenancy a claim rather than a fact.
    """
    return {
        "workspace_id": str(caller.workspace_id),
        "actor": caller.principal.model_dump(mode="json"),
    }
