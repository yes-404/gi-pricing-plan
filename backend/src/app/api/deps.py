"""Request dependencies: who is calling, and on whose behalf (FR-387, FR-388, FR-389, FR-390).

Three credential paths, tried in order, and every one of them can only *fail closed*:

1. `Authorization: Bearer <jwt>` — an OIDC access token, verified against the provider.
2. `Authorization: ApiKey <key>` / `X-API-Key` — a Service Account key.
3. Development headers — **local only**, and `Settings.require_startable` refuses to boot
   with them enabled in `uat` or `prod`.

With none of these configured or presented, the answer is `401`, never a default identity.

The workspace is not taken from the request. A caller states nothing about which workspace
it is acting in; the platform derives it from membership (users) or from the account's own
workspace (service accounts). An *unverified* header-supplied workspace would make the
scope a claim rather than a fact.

That is what stays refused, and it is narrower than it reads. OQ-648, decided
2026-08-23 (`07` FR-397), settled that a principal with several memberships names one
in a `Workspace-Id` header and the platform checks it against the memberships it already
holds: a choice among facts is not a claim. That check is built (W32-7): `require_caller`
declares the header and `_select_workspace` verifies it against the memberships the
platform holds, denying a workspace the principal does not belong to. What has not changed
is the rule the header serves — an *unverified* scope is still refused, and a caller with
several memberships and no selection is still refused rather than defaulted into one.

A workspace is *not* the tenant boundary — ADR-710 makes that the deployment, and one
deployment serves one tenant. What this scoping buys is that a home-pricing team cannot
read the motor book, which is worth having on its own; it is not what keeps two insurers
apart, and describing it that way would put weight on a check that was never load-bearing
for that.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends, Header, Request
from sqlalchemy import select

from app.auth.oidc import OidcVerifier
from app.auth.service import AuthenticatedIdentity, authenticate_api_key, authenticate_bearer
from app.config import Settings
from app.db.models import WorkspaceMemberRow
from app.db.session import Database
from app.errors import PlatformError
from model_schema import ActorKind, Principal

__all__ = ["WORKSPACE_ID_DESCRIPTION", "Caller", "Identity", "IdentityDep", "require_caller"]

#: Development-only header. Named so it cannot be mistaken for a supported mechanism.
#: Its former sibling `x-dev-workspace-id` is gone (W6b-11, 2026-08-26): the dev path
#: resolves the workspace from the same verified `Workspace-Id` header as every caller,
#: because a dev request must exercise the same selection a real one does.
DEV_PRINCIPAL_HEADER = "x-dev-principal-id"


@dataclass(frozen=True)
class Caller:
    """The authenticated principal and the workspace it is acting in (FR-16)."""

    principal: Principal
    workspace_id: UUID
    environments: frozenset[str] = frozenset()
    #: The environment the presented credential was scoped to (RL-916) — `None` for a
    #: bearer or development caller. `environments` above is unchanged: the account's
    #: granted set, still the field authorisation reads.
    environment: str | None = None
    permissions: frozenset[str] = frozenset()


def _settings(request: Request) -> Settings:
    settings: Settings = request.app.state.settings
    return settings


SettingsDep = Annotated[Settings, Depends(_settings)]


def _database(request: Request) -> Database:
    database: Database = request.app.state.database
    return database


DatabaseDep = Annotated[Database, Depends(_database)]


@dataclass(frozen=True)
class Identity:
    """An authenticated principal with no workspace selection made.

    `require_caller` resolves a selection and refuses rather than defaulting
    (`FR-397`); this does neither. It exists for the one surface a principal must
    reach before it has a selection — the switch endpoints in `me.py`.
    """

    principal: Principal
    workspaces: frozenset[UUID]


async def require_identity(
    request: Request,
    database: DatabaseDep,
    settings: SettingsDep,
) -> Identity:
    """Authenticate the caller without resolving a workspace selection."""
    # The same credential order `require_caller` uses (:112-127): bearer → apikey → dev.
    authorization = request.headers.get("authorization", "")
    scheme, _, credential = authorization.partition(" ")
    scheme = scheme.lower()

    if scheme == "bearer" and credential:
        verifier: OidcVerifier = request.app.state.oidc_verifier
        async with database.unit_of_work() as session:
            identity = await authenticate_bearer(session, verifier, credential)
        # `identity.workspaces` was read at authentication time; pass it through as-is
        # rather than inventing a second source (`test_workspace_selection.py:46-50`
        # re-authenticates for exactly this reason).
        return Identity(principal=identity.principal, workspaces=identity.workspaces)

    api_key = credential if scheme == "apikey" else request.headers.get("x-api-key")
    if api_key:
        async with database.unit_of_work() as session:
            identity = await authenticate_api_key(session, api_key)
        # A Service Account has exactly one workspace by construction — the single id
        # `authenticate_api_key` already read is its membership set.
        return Identity(principal=identity.principal, workspaces=identity.workspaces)

    return await _development_identity(request, settings, database)


async def _development_identity(
    request: Request, settings: Settings, database: Database
) -> Identity:
    """Local-only identity from headers, with the memberships from the database.

    The `x-dev-principal-id` half of `_development_caller` (:185-220), with no workspace
    resolution — the selection is not this dependency's job. Memberships are read the
    same way `authenticate_bearer` reads them, so a dev principal and a bearer principal
    answer the same list.
    """
    if not settings.dev_auth_enabled:
        raise PlatformError(
            "UNAUTHENTICATED",
            "Authentication required",
            401,
            "No credential was presented. Use an OIDC bearer token or a service account "
            "API key.",
        )

    principal_id = request.headers.get(DEV_PRINCIPAL_HEADER)
    if not principal_id:
        raise PlatformError(
            "UNAUTHENTICATED",
            "Authentication required",
            401,
            f"Development identity is enabled; supply {DEV_PRINCIPAL_HEADER}.",
        )

    try:
        principal = Principal(
            kind=ActorKind.USER, id=UUID(principal_id), display="dev@localhost"
        )
    except ValueError as exc:
        raise PlatformError(
            "UNAUTHENTICATED",
            "Authentication required",
            401,
            "Development identity headers must be UUIDs.",
        ) from exc

    async with database.unit_of_work() as session:
        rows = (
            (
                await session.execute(
                    select(WorkspaceMemberRow.workspace_id).where(
                        WorkspaceMemberRow.user_id == principal.id
                    )
                )
            )
            .scalars()
            .all()
        )
    return Identity(principal=principal, workspaces=frozenset(rows))


IdentityDep = Annotated[Identity, Depends(require_identity)]

#: Reused as the header's OpenAPI description on every operation, so the published contract
#: says the same thing in each place. A generated client is written against this text.
WORKSPACE_ID_DESCRIPTION = (
    "The workspace to act in, as a UUID. Required when the principal is a member of more "
    "than one (`07` FR-397); a principal with exactly one, and a Service Account, send "
    "nothing. Checked against the principal's own memberships: a workspace it does not "
    "belong to yields `403 WORKSPACE_SCOPE_DENIED`, and an absent selection with several "
    "memberships yields `403 WORKSPACE_SELECTION_REQUIRED`."
)


async def require_caller(
    request: Request,
    settings: SettingsDep,
    workspace_id: Annotated[
        str | None, Header(alias="Workspace-Id", description=WORKSPACE_ID_DESCRIPTION)
    ] = None,
) -> Caller:
    """Resolve the caller, or refuse."""
    # Taken as `str | None` and parsed here rather than annotated `UUID | None`: FastAPI
    # would answer a malformed UUID with a bare `422` outside the platform error
    # catalogue, and FR-397 requires the refusal to be a typed platform error.
    selected: UUID | None = None
    if workspace_id is not None:
        try:
            selected = UUID(workspace_id)
        except ValueError as exc:
            raise PlatformError(
                "WORKSPACE_SCOPE_DENIED",
                "Workspace scope denied",
                403,
                "The Workspace-Id header must be a UUID.",
            ) from exc

    authorization = request.headers.get("authorization", "")
    scheme, _, credential = authorization.partition(" ")
    scheme = scheme.lower()

    database: Database = request.app.state.database

    if scheme == "bearer" and credential:
        verifier: OidcVerifier = request.app.state.oidc_verifier
        async with database.unit_of_work() as session:
            identity = await authenticate_bearer(session, verifier, credential)
        return _select_workspace(identity, selected)

    api_key = credential if scheme == "apikey" else request.headers.get("x-api-key")
    if api_key:
        async with database.unit_of_work() as session:
            identity = await authenticate_api_key(session, api_key)
        return _select_workspace(identity, selected)

    # The dev path consumes the same `Workspace-Id` header with the same membership
    # check as the bearer and API-key paths above. An earlier version of this comment
    # said the dev path read "a different header for a different purpose" — that was
    # true before W6b-11 (2026-08-26) removed `x-dev-workspace-id`, and describes no
    # code that exists now.
    return await _development_caller(request, settings, database, selected)


def _select_workspace(identity: AuthenticatedIdentity, selected: UUID | None) -> Caller:
    """Collapse an authenticated identity to the one workspace it is acting in.

    Takes the header's **value**, not the `Request`. `require_caller` declares `Workspace-Id`
    as a parameter so that it appears in the published contract a client generates from, and
    a helper that then went behind the dependency's back to read the raw request would leave
    that declared parameter unused — which is how a documented header stops being the one the
    server actually reads.

    The selection is **checked, never trusted** (FR-396, FR-397). The invariant this
    module has carried since WK-658 — that a header-supplied workspace would make the scope a
    claim rather than a fact — refuses *trusting* the caller. A choice among memberships the
    platform already holds is not a claim; defaulting would be, which is why an absent
    selection is refused rather than resolved.
    """
    if not identity.workspaces:
        # FR-390 owns this branch and FR-396 does not touch it: no membership is a
        # different fact from an unmade choice, and it keeps its original code.
        raise PlatformError(
            "UNAUTHENTICATED",
            "No workspace access",
            403,
            "This principal is authenticated but is a member of no workspace. Access is "
            "granted explicitly (FR-390); it is never the default.",
        )
    if selected is not None:
        if selected not in identity.workspaces:
            raise PlatformError(
                "WORKSPACE_SCOPE_DENIED",
                "Workspace scope denied",
                403,
                "The Workspace-Id header names a workspace this principal is not a member "
                "of. The selection is checked against the memberships the platform holds "
                "(07 FR-397); it is never taken on trust.",
            )
        chosen = selected
    elif len(identity.workspaces) > 1:
        raise PlatformError(
            "WORKSPACE_SELECTION_REQUIRED",
            "Workspace selection required",
            403,
            "This principal belongs to more than one workspace. Name one in the "
            "Workspace-Id header (07 FR-397); the platform will not choose for you.",
        )
    else:
        chosen = next(iter(identity.workspaces))

    return Caller(
        principal=identity.principal,
        workspace_id=chosen,
        environments=identity.environments,
        environment=identity.environment,
        permissions=identity.permissions,
    )


async def _development_caller(
    request: Request, settings: Settings, database: Database, selected: UUID | None
) -> Caller:
    """Local-only caller, resolved to a workspace exactly like a bearer caller.

    Identification is `_development_identity`'s job; the selection is `_select_workspace`'s
    — the same check every other caller path runs, so a dev request is checked against the
    memberships the platform holds, never against a header pin.
    """
    identity = await _development_identity(request, settings, database)
    return _select_workspace(
        AuthenticatedIdentity(
            principal=identity.principal, workspaces=identity.workspaces
        ),
        selected,
    )


def job_identity(caller: Caller) -> dict[str, Any]:
    """Who asked, and in which workspace — carried in every domain Job's parameters.

    A handler receives only `row.parameters`, so without this it cannot attribute what it
    does, and every audit event a dataset job writes would read as "the system". That
    answers the wrong question: nobody asks whether the platform ingested a file.

    The workspace is included for the same reason and taken from the *caller*, never from
    the request body — a body-supplied workspace makes the scope a claim rather than a fact.
    """
    return {
        "workspace_id": str(caller.workspace_id),
        "actor": caller.principal.model_dump(mode="json"),
    }
