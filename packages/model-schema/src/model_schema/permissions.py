"""The permission vocabulary and the built-in roles (`06` §3.1, `00` §1.4).

> **FR-GOV-2** — Permissions are checked in the backend on every request against
> `(principal, permission, resource, scope)`. The frontend hides what a user cannot do; it
> never *enforces* it.

The vocabulary lives in `model-schema` because both sides need it and neither may invent
it: the backend enforces against it, and the frontend renders against the same list to
decide what to show. A permission string typed by hand in a Vue component is a permission
that exists nowhere else and silently grants nothing — or, worse, hides a control the user
does hold.

Roles are **platform objects** (FR-GOV-3): the platform ships the `00` §1.4 roles with
documented permission sets and supports custom roles composed from this same vocabulary.
Where role *membership* comes from — an identity provider's groups or an in-platform
assignment — is OQ-GOV-2 and is deliberately not settled here; FR-PLAT-4 already specifies
that mapping as configuration, and both answers need this model underneath.
"""

from __future__ import annotations

import enum
from typing import Final

__all__ = ["BUILTIN_ROLES", "READ_PERMISSIONS", "Permission", "ScopeType", "role_permissions"]


class Permission(enum.StrEnum):
    """Every permission the platform checks. Closed by design.

    A free-string permission is one nobody can enumerate, so no screen can list what a role
    grants and no test can assert a role does not grant something.
    """

    # Data (`01`)
    DATASET_READ = "dataset:read"
    DATASET_WRITE = "dataset:write"
    DATASET_VALIDATE = "dataset:validate"
    DATASET_ACKNOWLEDGE_WARNING = "dataset:acknowledge_warning"

    # Modelling (`02`)
    MODEL_READ = "model:read"
    MODEL_FIT = "model:fit"
    MODEL_SUBMIT = "model:submit"

    # Rating (`03`)
    RATING_READ = "rating:read"
    RATING_WRITE = "rating:write"
    RATING_SUBMIT = "rating:submit"
    RATING_COMPILE = "rating:compile"

    # Governance (`06`)
    APPROVAL_DECIDE = "approval:decide"
    DEPLOYMENT_PROMOTE = "deployment:promote"
    AUDIT_READ = "audit:read"

    # Scoring (`03`, `07`) — the only permissions a Service Account may hold (FR-GOV-6)
    SCORE_EXECUTE = "score:execute"
    SCORE_BATCH = "score:batch"

    # Platform (`07`)
    JOB_READ = "job:read"
    JOB_CANCEL = "job:cancel"
    SETTINGS_READ = "settings:read"

    # Administration
    ADMIN_MANAGE_ROLES = "admin:manage_roles"
    ADMIN_MANAGE_SETTINGS = "admin:manage_settings"
    ADMIN_MANAGE_ENVIRONMENTS = "admin:manage_environments"
    ADMIN_MANAGE_SERVICE_ACCOUNTS = "admin:manage_service_accounts"
    ADMIN_BREAK_GLASS = "admin:break_glass"


#: Permissions that only read. FR-GOV-5 makes the Auditor role exactly this set: "read
#: everything, write nothing, including the audit log, superseded artifacts and archived
#: datasets. No role, including Admin, can hide an artifact from an Auditor." Deriving the
#: role from this set rather than listing it means a new read permission is granted to
#: Auditor automatically — the failure mode being an artifact type an auditor cannot see.
READ_PERMISSIONS: Final[frozenset[Permission]] = frozenset(
    {
        Permission.DATASET_READ,
        Permission.MODEL_READ,
        Permission.RATING_READ,
        Permission.AUDIT_READ,
        Permission.JOB_READ,
        Permission.SETTINGS_READ,
    }
)


class ScopeType(enum.StrEnum):
    """What a role assignment applies to (FR-GOV-4).

    "so a motor actuary cannot approve home pricing without an explicit assignment" — the
    reason scope exists at all, and the reason a workspace-wide assignment must be a
    deliberate choice rather than the only option.
    """

    WORKSPACE = "workspace"
    DATASET = "dataset"
    MODEL_FAMILY = "model_family"
    RATING_ALGORITHM = "rating_algorithm"


def _analyst() -> frozenset[Permission]:
    return frozenset(
        {
            Permission.DATASET_READ,
            Permission.DATASET_WRITE,
            Permission.DATASET_VALIDATE,
            Permission.MODEL_READ,
            Permission.MODEL_FIT,
            Permission.RATING_READ,
            Permission.RATING_WRITE,
            Permission.RATING_COMPILE,
            Permission.JOB_READ,
            Permission.JOB_CANCEL,
            Permission.SETTINGS_READ,
        }
    )


#: The `00` §1.4 roles with their default permission sets (FR-GOV-3).
#:
#: **Admin does not hold `approval:decide` or `deployment:promote`.** The actor definition
#: is "manages users, roles, environments, reference data, and system settings" — an
#: administrator who could also approve would be a single principal able to grant itself an
#: approval right and then use it, which is the separation FR-GOV-11 exists to enforce.
#: Elevation for a genuine emergency is break-glass (FR-GOV-8), which is time-boxed and
#: leaves a mark.
BUILTIN_ROLES: Final[dict[str, frozenset[Permission]]] = {
    "analyst": _analyst(),
    "pricing_actuary": _analyst()
    | {
        Permission.DATASET_ACKNOWLEDGE_WARNING,
        Permission.MODEL_SUBMIT,
        Permission.RATING_SUBMIT,
    },
    "approver": frozenset(READ_PERMISSIONS) | {Permission.APPROVAL_DECIDE},
    "deployer": frozenset(READ_PERMISSIONS) | {Permission.DEPLOYMENT_PROMOTE},
    "auditor": frozenset(READ_PERMISSIONS),
    "admin": frozenset(READ_PERMISSIONS)
    | {
        Permission.ADMIN_MANAGE_ROLES,
        Permission.ADMIN_MANAGE_SETTINGS,
        Permission.ADMIN_MANAGE_ENVIRONMENTS,
        Permission.ADMIN_MANAGE_SERVICE_ACCOUNTS,
        Permission.ADMIN_BREAK_GLASS,
    },
}


def role_permissions(role: str) -> frozenset[Permission]:
    """Permissions for a built-in role. Raises for an unknown one."""
    try:
        return BUILTIN_ROLES[role]
    except KeyError:
        raise ValueError(
            f"unknown built-in role {role!r}; custom roles are stored, not defined here"
        ) from None
