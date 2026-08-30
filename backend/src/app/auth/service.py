"""Turning a credential into a Caller (FR-PLAT-1..4, FR-PLAT-6).

Two credential types, one outcome:

* a **bearer token** from the identity provider — a User;
* an **API key** — a Service Account, scoped to named environments and to scoring.

Everything that fails here fails the same way: `401` with a code, and an audit event
(FR-PLAT-6). The response never says *which* check failed. "Expired" versus "unknown key"
versus "wrong signature" tells an attacker what to change next, and tells a legitimate
caller nothing they can act on that the trace id does not already give them.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.api_keys import parse_key, verify_secret
from app.auth.oidc import OidcVerifier, TokenClaims, TokenRejectedError
from app.db.models import ApiKeyRow, ServiceAccountRow, UserRow, WorkspaceMemberRow
from app.errors import PlatformError
from app.observability.logging import get_logger
from app.platform import audit
from model_schema import ActorKind, JobSource, Principal

__all__ = ["AuthenticatedIdentity", "authenticate_api_key", "authenticate_bearer"]

_log = get_logger("app.auth")

#: The Principal an authentication *failure* is recorded against. The caller is by
#: definition unidentified, and attributing the event to the identity they claimed would
#: put a failed login on an innocent user's record.
_UNKNOWN = Principal(kind=ActorKind.SYSTEM, display="unauthenticated")


class AuthenticatedIdentity:
    """A verified principal and the workspaces it may act in."""

    __slots__ = ("environment", "environments", "permissions", "principal", "workspaces")

    def __init__(
        self,
        principal: Principal,
        workspaces: frozenset[UUID],
        *,
        environments: frozenset[str] = frozenset(),
        environment: str | None = None,
        permissions: frozenset[str] = frozenset(),
    ) -> None:
        self.principal = principal
        self.workspaces = workspaces
        self.environments = environments
        #: The environment the *presented credential* was scoped to (Ruling 44) — never a
        #: derivation from `environments`, the account's granted set. `None` for a bearer or
        #: development caller, and for any credential type minted before this field existed.
        self.environment = environment
        self.permissions = permissions


def _unauthenticated(code: str = "UNAUTHENTICATED") -> PlatformError:
    return PlatformError(
        code,
        "Authentication failed",
        401,
        "The credential presented was not accepted. Quote the trace id when reporting it.",
    )


async def _audit_auth_failure(
    session: AsyncSession, *, workspace_id: UUID | None, action: str, detail: str
) -> None:
    """Record a failed authentication (FR-PLAT-6, `06` FR-GOV-20).

    Skipped when no workspace can be determined: the audit log is chained per workspace,
    and inventing one to hold an event would corrupt a real chain. Those failures are
    logged instead — an unauthenticated caller has no workspace by definition, and a
    workspace's audit log is not the right place for traffic that never reached it.
    """
    if workspace_id is None:
        _log.warning("authentication failed", extra={"action": action, "reason": detail})
        return
    await audit.record(
        session,
        workspace_id=workspace_id,
        actor=_UNKNOWN,
        source=JobSource.API,
        action=action,
        entity_ref="principal:unauthenticated@1",
        after={"reason": detail},
    )


async def authenticate_bearer(
    session: AsyncSession, verifier: OidcVerifier, token: str
) -> AuthenticatedIdentity:
    """Verify an OIDC access token and resolve the user (FR-PLAT-1, FR-PLAT-4)."""
    try:
        claims = verifier.verify(token)
    except TokenRejectedError as exc:
        _log.info("bearer token rejected", extra={"reason": exc.reason})
        raise _unauthenticated("TOKEN_EXPIRED" if "Expired" in exc.reason else
                               "UNAUTHENTICATED") from exc

    user = await _upsert_user(session, claims, issuer=verifier.issuer)

    memberships = (
        await session.execute(
            select(WorkspaceMemberRow.workspace_id).where(
                WorkspaceMemberRow.user_id == user.id
            )
        )
    ).scalars().all()

    # FR-PLAT-4: no mapped access means *no* access. An authenticated user with no
    # membership is a real, known user who may act nowhere — which is the correct state
    # until governance grants them something (W3).
    return AuthenticatedIdentity(
        principal=Principal(
            kind=ActorKind.USER, id=user.id, display=user.email or claims.subject
        ),
        workspaces=frozenset(memberships),
    )


async def _upsert_user(
    session: AsyncSession, claims: TokenClaims, *, issuer: str
) -> UserRow:
    """Create the user on first login, then keep the display fields current (FR-PLAT-4).

    Keyed on `(issuer, subject)`, never on email: an email change would otherwise create a
    second user and orphan everything the first one did.

    **This runs on every bearer request, not only at login.** `require_caller` calls
    `authenticate_bearer` per request (`app/api/deps.py`), so the `last_login_at` written
    below is stamped each time and records last-*seen*. Nothing reads the column today,
    which is why the name has cost nothing so far; whoever first reports on it — a
    dormant-account or last-access view under `06` — has to decide whether the intent was
    login or activity, because the column as written cannot answer the first.
    """
    user = (
        await session.execute(
            select(UserRow).where(
                UserRow.issuer == issuer, UserRow.subject == claims.subject
            )
        )
    ).scalar_one_or_none()

    if user is None:
        user = UserRow(issuer=issuer, subject=claims.subject)
        session.add(user)

    user.email = claims.email
    user.display_name = claims.name
    user.last_login_at = datetime.now(UTC)
    await session.flush()
    return user


async def authenticate_api_key(
    session: AsyncSession, presented: str
) -> AuthenticatedIdentity:
    """Verify a Service Account key (FR-PLAT-3, FR-PLAT-30)."""
    parsed = parse_key(presented)
    if parsed is None:
        await _audit_auth_failure(
            session, workspace_id=None, action="principal.auth_failed", detail="malformed key"
        )
        raise _unauthenticated("API_KEY_INVALID")

    key = (
        await session.execute(select(ApiKeyRow).where(ApiKeyRow.prefix == parsed.prefix))
    ).scalar_one_or_none()

    if key is None or not verify_secret(parsed.secret, key.secret_hash):
        # Same outcome for "no such prefix" and "wrong secret". Distinguishing them turns
        # the prefix into an oracle for which keys exist.
        await _audit_auth_failure(
            session, workspace_id=None, action="principal.auth_failed", detail="invalid key"
        )
        raise _unauthenticated("API_KEY_INVALID")

    account = await session.get(ServiceAccountRow, key.service_account_id)
    if account is None or account.archived_at is not None:
        await _audit_auth_failure(
            session,
            workspace_id=account.workspace_id if account else None,
            action="principal.auth_failed",
            detail="service account archived",
        )
        raise _unauthenticated("API_KEY_INVALID")

    now = datetime.now(UTC)
    if key.revoked_at is not None:
        await _audit_auth_failure(
            session,
            workspace_id=account.workspace_id,
            action="principal.auth_failed",
            detail="key revoked",
        )
        raise _unauthenticated("API_KEY_INVALID")
    if key.expires_at <= now:
        await _audit_auth_failure(
            session,
            workspace_id=account.workspace_id,
            action="principal.auth_failed",
            detail="key expired",
        )
        raise _unauthenticated("API_KEY_EXPIRED")

    # FR-PLAT-30: a `uat` key can never score against `prod`. Checked against the account's
    # granted environments, not the string inside the key — the key is attacker-supplied
    # and its environment field is a label, not an authorisation.
    if parsed.environment not in set(account.environments):
        await _audit_auth_failure(
            session,
            workspace_id=account.workspace_id,
            action="principal.auth_failed",
            detail="environment not granted",
        )
        raise _unauthenticated("ENVIRONMENT_SCOPE_DENIED")

    key.last_used_at = now
    await session.flush()

    return AuthenticatedIdentity(
        principal=Principal(
            kind=ActorKind.SERVICE_ACCOUNT, id=account.id, display=account.slug
        ),
        workspaces=frozenset({account.workspace_id}),
        environments=frozenset(account.environments),
        # Ruling 44: the environment *this key was presented for* (already verified above,
        # `:212`), not a tie-break over the granted set — `environments` keeps its existing
        # meaning and use in authorisation; this is a separate, single-valued fact.
        environment=parsed.environment,
        permissions=frozenset(account.permissions),
    )
