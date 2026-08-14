"""Request dependencies: who is calling, and on whose behalf.

**OIDC is not implemented yet** (FR-PLAT-1..4, the next W2 slice). Until it is, this module
is deliberately shaped so that the absence of authentication is a *refusal*, not an
omission: `require_principal` returns `401 UNAUTHENTICATED` unless development identity is
explicitly switched on, and `Settings.require_startable` refuses to boot with it on in
`uat` or `prod`.

Every route that reads or changes workspace data depends on this, so a route added later
inherits the refusal by default rather than having to remember to ask for it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request

from app.config import Settings
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


def _settings(request: Request) -> Settings:
    settings: Settings = request.app.state.settings
    return settings


SettingsDep = Annotated[Settings, Depends(_settings)]


def require_caller(request: Request, settings: SettingsDep) -> Caller:
    """Resolve the caller, or refuse.

    The unauthenticated path is the default and returns 401 with a code the frontend can
    branch on, rather than a 500 from a missing attribute — an endpoint whose auth is
    "not wired up yet" must fail closed and say so.
    """
    if not settings.dev_auth_enabled:
        raise PlatformError(
            "UNAUTHENTICATED",
            "Authentication required",
            401,
            "This deployment has no identity provider configured. OIDC login "
            "(FR-PLAT-1) is not yet implemented in this build.",
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
