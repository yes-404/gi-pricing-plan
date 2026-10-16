"""Route-level permission enforcement (`06` FR-342, FR-343).

    @router.get("", dependencies=[Depends(requires(Permission.JOB_READ))])

A dependency rather than a call inside each handler, so the requirement is visible in the
route definition and appears in the generated contract's description. A check buried three
lines into a handler is one a reviewer has to go looking for, and one a new endpoint
forgets.

**Development identity grants no permissions.** It authenticates and nothing more. The
alternative — treating the dev principal as an administrator — would make every route test
pass without exercising a single permission check, which is the shape of test that reports
coverage it does not have. Tests grant roles explicitly, as a deployment would.

Resource-scoped checks (FR-345) stay inside handlers, because the resource id is not
known until the path parameter is resolved and often not until a row is loaded.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Annotated

from uuid import UUID

from fastapi import Depends, Request

from app.api.deps import Caller, Identity, IdentityDep, SettingsDep, require_caller
from app.config import Settings
from app.db.session import Database
from app.platform import rate_limit, rbac
from model_schema import Permission, Principal

__all__ = [
    "MANAGEMENT_RATE_LIMIT_SETTING",
    "MANAGEMENT_COUNTED_ATTRIBUTE",
    "PERMISSION_ATTRIBUTE",
    "CallerDep",
    "CountAfterCheck",
    "counted_caller",
    "counted_identity",
    "management_counter",
    "requires",
]

#: Stamped on the dependency `requires()` builds, so a test can ask a route which
#: permission it enforces instead of inferring it from a status code.
#:
#: A response-only sweep cannot tell "refused because the caller lacks the permission"
#: from "refused because the body was invalid" — and a `POST` with an empty body answers
#: 422 either way, so a route that enforced nothing would pass. Downgrading
#: `requires(Perm.DATASET_READ)` to `require_caller` left all 609 tests green; this
#: attribute is what makes that visible.
PERMISSION_ATTRIBUTE = "__gip_permission__"

#: Stamped on the dependency `requires()` builds with whether it counts against the management
#: limit, so a test can tell a route that can answer `429` from one that cannot without
#: inferring it from a status code (the lead's amendment, "an operation declares 429 IFF it
#: can return 429").
MANAGEMENT_COUNTED_ATTRIBUTE = "__gip_management_counted__"

CallerDep = Annotated[Caller, Depends(require_caller)]


def _database(request: Request) -> Database:
    database: Database = request.app.state.database
    return database


DatabaseDep = Annotated[Database, Depends(_database)]


#: FR-452's management-API limit (`RL-1687`): the Setting that is its limit.
MANAGEMENT_RATE_LIMIT_SETTING = "platform.default_management_rate_limit_rps"

_COUNTED_FLAG = "management_rate_limit_counted"


async def _count_management_request(
    request: Request,
    principal: Principal,
    workspace_id: UUID | None,
    environment: str | None,
    database: Database,
    settings: Settings,
) -> None:
    """Count one authenticated management request (FR-452, `RL-1687` (1a), (2a), (3a)).

    Run by the dependencies every authenticated `/api/v1` route outside the `/score`
    family goes through, `requires()` (after its permission check), `counted_caller()`
    (a route with no permission) and `counted_identity()` (the two routes a principal
    reaches before it has a workspace), so a `401` or a `403` is never counted and a route
    added later is counted with no edit. At most once per request: a route may carry both.
    `account_limit` is `None` because `rate_limit_rps` is the scoring limit only (3a).
    `workspace_id` is `None` for an identity route: the Setting then resolves without its
    workspace layer (the maintainer's (by delegation) entry "2026-10-16 10:31:43 BST",
    DP-S4-ME (A)).
    """
    if getattr(request.state, _COUNTED_FLAG, False):
        return
    setattr(request.state, _COUNTED_FLAG, True)
    await rate_limit.enforce(
        request.app.state.rate_limiter,
        database,
        settings,
        route="management",
        default_setting=MANAGEMENT_RATE_LIMIT_SETTING,
        workspace_id=workspace_id,
        environment=environment,
        principal=principal,
        account_limit=None,
    )


async def _count_caller(
    request: Request, caller: Caller, database: Database, settings: Settings
) -> None:
    await _count_management_request(
        request, caller.principal, caller.workspace_id, caller.environment, database, settings
    )


async def counted_caller(
    request: Request, caller: CallerDep, database: DatabaseDep, settings: SettingsDep
) -> Caller:
    """`require_caller` plus the management count, for an authenticated route that declares
    no permission (`/me`, `/approval-requests`, ...). A route with a permission uses
    `requires()`, which counts after its check; a route whose service decides the permission
    uses `management_counter()`."""
    await _count_caller(request, caller, database, settings)
    return caller


async def counted_identity(
    request: Request, identity: IdentityDep, database: DatabaseDep, settings: SettingsDep
) -> Identity:
    """`require_identity` plus the management count, for the two routes a principal reaches
    before it has a workspace selection (`GET /me/workspaces`, `POST /me/workspace`).

    Counted with `workspace_id=None` and no Environment (an identity has neither): the limit
    is the environment-variable layer, else the default; a workspace override does not apply
    (the maintainer's (by delegation) entry "2026-10-16 10:31:43 BST", DP-S4-ME (A))."""
    await _count_management_request(
        request, identity.principal, None, None, database, settings
    )
    return identity


#: What a service calls once its own permission check has passed (`RL-1687` (1a)).
CountAfterCheck = Callable[[], Awaitable[None]]


async def management_counter(
    request: Request, caller: CallerDep, database: DatabaseDep, settings: SettingsDep
) -> CountAfterCheck:
    """For a route whose permission is decided inside its service (it depends on the body or
    on the resource: a `sql` rule needs `admin:manage_settings`, a deployment needs
    `deployment:promote` on the Environment the path names). Authenticates the caller and
    returns the count **without running it**: the service awaits it right after its
    permission check, so a `403` is never counted. The check stays in the service."""

    async def count() -> None:
        await _count_caller(request, caller, database, settings)

    return count


def requires(
    permission: Permission, *, management_counted: bool = True
) -> Callable[..., Awaitable[Caller]]:
    """Build a dependency that refuses unless the caller holds `permission`.

    Returns the `Caller` so a handler can depend on this instead of `require_caller` and
    have both the identity and the check in one place. Once the check passes it counts the
    request against FR-452's management limit; `management_counted=False` is for the
    `/score` family only, which the scoring limit counts instead (`RL-1687`).
    """

    async def dependency(
        request: Request, caller: CallerDep, database: DatabaseDep, settings: SettingsDep
    ) -> Caller:
        async with database.session() as session:
            await rbac.require_permission(
                session,
                workspace_id=caller.workspace_id,
                principal=caller.principal,
                permission=permission,
                # RL-924: the set this credential actually authenticated with, passed
                # rather than re-derived. A Service Account's grants live on its own record
                # and reach no role, so without this a permission only a Service Account may
                # hold (FR-347) can never be satisfied.
                credential_permissions=caller.permissions,
            )
        if management_counted:
            await _count_caller(request, caller, database, settings)
        return caller

    setattr(dependency, PERMISSION_ATTRIBUTE, permission)
    setattr(dependency, MANAGEMENT_COUNTED_ATTRIBUTE, management_counted)
    return dependency
