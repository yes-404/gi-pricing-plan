"""Turning a credential into a Caller (FR-387, FR-388, FR-389, FR-390, FR-392).

Two credential types, one outcome:

* a **bearer token** from the identity provider — a User;
* an **API key** — a Service Account, scoped to named environments and to scoring.

Everything that fails here fails the same way: `401` with a code, counted by reason and,
when the credential resolved to a workspace, an audit event (FR-392) that the caller writes
after the authentication transaction has ended (see `AuthenticationFailed`). The response
never says *which* check failed. "Expired" versus "unknown key"
versus "wrong signature" tells an attacker what to change next, and tells a legitimate
caller nothing they can act on that the trace id does not already give them.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.api_keys import parse_key, verify_secret
from app.auth.oidc import OidcVerifier, TokenClaims, TokenRejectedError
from app.db.models import ApiKeyRow, ServiceAccountRow, UserRow, WorkspaceMemberRow
from app.errors import PlatformError
from app.observability.logging import get_logger
from app.observability.metrics import auth_failures
from app.platform import audit
from model_schema import ActorKind, JobSource, Principal

__all__ = [
    "AuthFailureReason",
    "AuthenticatedIdentity",
    "AuthenticationFailed",
    "authenticate_api_key",
    "authenticate_bearer",
    "record_auth_failure",
]

_log = get_logger("app.auth")

#: RL-1685 (PL-1454 DP-1 (b)): the longest a key's `last_used_at` may lag the real last use.
LAST_USED_WRITE_INTERVAL = timedelta(seconds=60)

#: The Principal an authentication *failure* is recorded against. The caller is by
#: definition unidentified, and attributing the event to the identity they claimed would
#: put a failed login on an innocent user's record.
_UNKNOWN = Principal(kind=ActorKind.SYSTEM, display="unauthenticated")


class AuthenticatedIdentity:
    """A verified principal and the workspaces it may act in."""

    __slots__ = (
        "environment",
        "environments",
        "permissions",
        "principal",
        "rate_limit_rps",
        "workspaces",
    )

    def __init__(
        self,
        principal: Principal,
        workspaces: frozenset[UUID],
        *,
        environments: frozenset[str] = frozenset(),
        environment: str | None = None,
        permissions: frozenset[str] = frozenset(),
        rate_limit_rps: int | None = None,
    ) -> None:
        self.principal = principal
        self.workspaces = workspaces
        self.environments = environments
        #: The environment the *presented credential* was scoped to (RL-916) — never a
        #: derivation from `environments`, the account's granted set. `None` for a bearer or
        #: development caller, and for any credential type minted before this field existed.
        self.environment = environment
        self.permissions = permissions
        #: The Service Account's own scoring rate limit (FR-452, `RL-1347` rule 2), read from
        #: the account row this authentication already loads. `None` for every other kind of
        #: Principal, and for an account that sets none.
        self.rate_limit_rps = rate_limit_rps


class AuthFailureReason(StrEnum):
    """The closed label set of `gip_auth_failures_total` (`07` FR-392, PL-1739 DP-3).

    Exactly eight members, and never the presented input: an unknown prefix and a wrong
    secret share `INVALID_KEY`, so the label is no oracle for which keys exist.
    """

    MALFORMED_KEY = "malformed_key"
    INVALID_KEY = "invalid_key"
    ACCOUNT_ARCHIVED = "account_archived"
    KEY_REVOKED = "key_revoked"
    KEY_EXPIRED = "key_expired"
    ENVIRONMENT_NOT_GRANTED = "environment_not_granted"
    BEARER_EXPIRED = "bearer_expired"
    BEARER_REJECTED = "bearer_rejected"


class AuthenticationFailed(PlatformError):  # noqa: N818 - named by PL-1739; a 401, not an Error
    """A `401` that also says what to record about it (FR-392).

    Authentication no longer writes its own failure row: the write would be flushed inside
    a transaction that this very exception rolls back. The caller catches it, lets the
    authentication transaction end, and calls `record_auth_failure` in one of its own.
    `workspace_id` is the workspace the credential resolved to, or `None` when it resolved
    to none.
    """

    def __init__(
        self, code: str, reason: AuthFailureReason, workspace_id: UUID | None = None
    ) -> None:
        super().__init__(
            code,
            "Authentication failed",
            401,
            "The credential presented was not accepted. Quote the trace id when reporting it.",
        )
        self.reason = reason
        self.workspace_id = workspace_id


async def record_auth_failure(session: AsyncSession, failure: AuthenticationFailed) -> None:
    """Count a failed authentication and, when it reached a workspace, audit it (FR-392).

    The counter moves first, so a failing audit write is still counted (`07` FR-392, DP-2).
    The write is not wrapped in `try/except`: a lost row must be a `5xx`, never a silent
    `401` (NFR-519, `platform/audit.py` module docstring).

    `session` must be inside a transaction of its own that holds nothing else; the caller
    commits it. Nothing is written when no workspace can be determined: the audit log is
    chained per workspace, and inventing one would corrupt a real chain. Those failures
    are logged instead — a caller who reached no workspace has no audit log to be in.
    """
    reason = AuthFailureReason(failure.reason)  # a non-member raises before anything moves
    auth_failures.labels(reason=reason.value).inc()
    if failure.workspace_id is None:
        _log.warning(
            "authentication failed",
            extra={"action": "principal.auth_failed", "reason": reason.value},
        )
        return
    await audit.record(
        session,
        workspace_id=failure.workspace_id,
        actor=_UNKNOWN,
        source=JobSource.API,
        action="principal.auth_failed",
        entity_ref="principal:unauthenticated@1",
        after={"reason": _DETAIL[reason]},
    )


#: The `after.reason` text of each keyed-workspace row: the four reasons that reach a workspace.
_DETAIL = {
    AuthFailureReason.ACCOUNT_ARCHIVED: "service account archived",
    AuthFailureReason.KEY_REVOKED: "key revoked",
    AuthFailureReason.KEY_EXPIRED: "key expired",
    AuthFailureReason.ENVIRONMENT_NOT_GRANTED: "environment not granted",
}


async def authenticate_bearer(
    session: AsyncSession, verifier: OidcVerifier, token: str
) -> AuthenticatedIdentity:
    """Verify an OIDC access token and resolve the user (FR-387, FR-390)."""
    try:
        claims = verifier.verify(token)
    except TokenRejectedError as exc:
        expired = "Expired" in exc.reason
        raise AuthenticationFailed(
            "TOKEN_EXPIRED" if expired else "UNAUTHENTICATED",
            AuthFailureReason.BEARER_EXPIRED if expired else AuthFailureReason.BEARER_REJECTED,
        ) from exc

    user = await _upsert_user(session, claims, issuer=verifier.issuer)

    memberships = (
        await session.execute(
            select(WorkspaceMemberRow.workspace_id).where(
                WorkspaceMemberRow.user_id == user.id
            )
        )
    ).scalars().all()

    # FR-390: no mapped access means *no* access. An authenticated user with no
    # membership is a real, known user who may act nowhere — which is the correct state
    # until governance grants them something (WK-659).
    return AuthenticatedIdentity(
        principal=Principal(
            kind=ActorKind.USER, id=user.id, display=user.email or claims.subject
        ),
        workspaces=frozenset(memberships),
    )


async def _upsert_user(
    session: AsyncSession, claims: TokenClaims, *, issuer: str
) -> UserRow:
    """Create the user on first login, then keep the display fields current (FR-390).

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
    """Verify a Service Account key (FR-389, FR-430)."""
    parsed = parse_key(presented)
    if parsed is None:
        raise AuthenticationFailed("API_KEY_INVALID", AuthFailureReason.MALFORMED_KEY)

    key = (
        await session.execute(select(ApiKeyRow).where(ApiKeyRow.prefix == parsed.prefix))
    ).scalar_one_or_none()

    if key is None or not verify_secret(parsed.secret, key.secret_hash):
        # Same outcome for "no such prefix" and "wrong secret". Distinguishing them turns
        # the prefix into an oracle for which keys exist.
        raise AuthenticationFailed("API_KEY_INVALID", AuthFailureReason.INVALID_KEY)

    account = await session.get(ServiceAccountRow, key.service_account_id)
    if account is None or account.archived_at is not None:
        raise AuthenticationFailed(
            "API_KEY_INVALID",
            AuthFailureReason.ACCOUNT_ARCHIVED,
            account.workspace_id if account else None,
        )

    now = datetime.now(UTC)
    if key.revoked_at is not None:
        raise AuthenticationFailed(
            "API_KEY_INVALID", AuthFailureReason.KEY_REVOKED, account.workspace_id
        )
    if key.expires_at <= now:
        raise AuthenticationFailed(
            "API_KEY_EXPIRED", AuthFailureReason.KEY_EXPIRED, account.workspace_id
        )

    # FR-430: a `uat` key can never score against `prod`. Checked against the account's
    # granted environments, not the string inside the key — the key is attacker-supplied
    # and its environment field is a label, not an authorisation.
    if parsed.environment not in set(account.environments):
        raise AuthenticationFailed(
            "ENVIRONMENT_SCOPE_DENIED",
            AuthFailureReason.ENVIRONMENT_NOT_GRANTED,
            account.workspace_id,
        )

    # RL-1685 (PL-1454 DP-1 (b)): `last_used_at` is a "when was this key last seen" stamp for
    # an operator, not an audit trail, so it is written only when it is unset or older than
    # `LAST_USED_WRITE_INTERVAL`. An UPDATE on every request is a commit, a row lock and a
    # WAL record per quote, on the hot path of NFR-489.
    if key.last_used_at is None or now - key.last_used_at >= LAST_USED_WRITE_INTERVAL:
        key.last_used_at = now

    return AuthenticatedIdentity(
        principal=Principal(
            kind=ActorKind.SERVICE_ACCOUNT, id=account.id, display=account.slug
        ),
        workspaces=frozenset({account.workspace_id}),
        environments=frozenset(account.environments),
        # RL-916: the environment *this key was presented for* (already verified above,
        # `:212`), not a tie-break over the granted set — `environments` keeps its existing
        # meaning and use in authorisation; this is a separate, single-valued fact.
        environment=parsed.environment,
        permissions=frozenset(account.permissions),
        rate_limit_rps=account.rate_limit_rps,
    )
