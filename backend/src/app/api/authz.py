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

from fastapi import Depends, Request

from app.api.deps import Caller, require_caller
from app.db.session import Database
from app.platform import rbac
from model_schema import Permission

__all__ = ["PERMISSION_ATTRIBUTE", "requires"]

#: Stamped on the dependency `requires()` builds, so a test can ask a route which
#: permission it enforces instead of inferring it from a status code.
#:
#: A response-only sweep cannot tell "refused because the caller lacks the permission"
#: from "refused because the body was invalid" — and a `POST` with an empty body answers
#: 422 either way, so a route that enforced nothing would pass. Downgrading
#: `requires(Perm.DATASET_READ)` to `require_caller` left all 609 tests green; this
#: attribute is what makes that visible.
PERMISSION_ATTRIBUTE = "__gip_permission__"

CallerDep = Annotated[Caller, Depends(require_caller)]


def _database(request: Request) -> Database:
    database: Database = request.app.state.database
    return database


DatabaseDep = Annotated[Database, Depends(_database)]


def requires(permission: Permission) -> Callable[..., Awaitable[Caller]]:
    """Build a dependency that refuses unless the caller holds `permission`.

    Returns the `Caller` so a handler can depend on this instead of `require_caller` and
    have both the identity and the check in one place.
    """

    async def dependency(caller: CallerDep, database: DatabaseDep) -> Caller:
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
        return caller

    setattr(dependency, PERMISSION_ATTRIBUTE, permission)
    return dependency
