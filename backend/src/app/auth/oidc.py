"""OIDC access-token verification (FR-PLAT-1, FR-PLAT-2).

The platform stores no passwords and issues no tokens. It verifies bearer tokens minted by
an external identity provider, which means the entire security of user authentication is
this file getting five things right:

1. **The signature**, against the provider's published JWKS.
2. **The algorithm**, restricted to asymmetric families. Accepting `HS256` alongside an
   RSA key set is the classic algorithm-confusion attack: the *public* key becomes an HMAC
   secret, and anyone who can read the JWKS can mint tokens.
3. **The issuer**, so a token from some other provider the service can reach is refused.
4. **The audience**, so a token minted for a different client of the same provider is not
   accepted here.
5. **Expiry**, with no leeway by default — a token is valid until it is not.

`none` is never in the allow-list, and the key set is fetched over TLS.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Final

import jwt
from jwt import PyJWKClient
from jwt.exceptions import InvalidTokenError

from app.config import Settings
from app.observability.logging import get_logger

__all__ = ["ALLOWED_ALGORITHMS", "OidcVerifier", "TokenClaims", "TokenRejectedError"]

_log = get_logger("app.auth.oidc")

#: Asymmetric only. See point 2 in the module docstring.
ALLOWED_ALGORITHMS: Final[list[str]] = ["RS256", "RS384", "RS512", "ES256", "ES384"]


class TokenRejectedError(Exception):
    """The token is not acceptable. The reason is logged, never returned.

    A verifier that tells a caller *why* their token failed tells an attacker which of
    issuer, audience, signature or expiry to fix next.
    """

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True)
class TokenClaims:
    """The claims the platform maps to a Principal (FR-PLAT-4)."""

    subject: str
    email: str | None
    name: str | None
    groups: tuple[str, ...]
    raw: dict[str, Any]


class OidcVerifier:
    """Verifies access tokens against a provider's JWKS.

    The key set is cached for `oidc_jwks_ttl_s`. Not fetching it per request is not only a
    latency matter: an identity provider that rate-limits the endpoint would otherwise make
    the platform's own traffic the reason logins fail.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: PyJWKClient | None = None
        self._fetched_at = 0.0

    @property
    def issuer(self) -> str:
        """The configured issuer. Users are keyed on `(issuer, subject)`, never on email."""
        return self._settings.oidc_issuer

    def _jwk_client(self) -> PyJWKClient:
        now = time.monotonic()
        if self._client is None or now - self._fetched_at > self._settings.oidc_jwks_ttl_s:
            # `lifespan` on PyJWKClient caches inside the client; the outer TTL bounds how
            # long a *revoked* signing key stays trusted, which the inner cache does not.
            self._client = PyJWKClient(
                self._settings.oidc_jwks_url,
                cache_keys=True,
                lifespan=self._settings.oidc_jwks_ttl_s,
            )
            self._fetched_at = now
        return self._client

    def verify(self, token: str) -> TokenClaims:
        """Verify a bearer token and return its claims, or raise `TokenRejectedError`."""
        if not self._settings.oidc_configured:
            raise TokenRejectedError("no identity provider is configured")

        try:
            signing_key = self._jwk_client().get_signing_key_from_jwt(token)
        except Exception as exc:
            # A JWKS fetch failure and an unknown `kid` both land here. Neither is
            # distinguishable to the caller, and the operator gets the type in the log.
            _log.warning(
                "could not resolve a signing key", extra={"error_type": type(exc).__name__}
            )
            raise TokenRejectedError(f"signing key unavailable: {type(exc).__name__}") from exc

        try:
            claims: dict[str, Any] = jwt.decode(
                token,
                signing_key.key,
                algorithms=ALLOWED_ALGORITHMS,
                issuer=self._settings.oidc_issuer,
                audience=self._settings.oidc_audience,
                options={
                    "require": ["exp", "iat", "iss", "aud", "sub"],
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iss": True,
                    "verify_aud": True,
                },
                leeway=0,
            )
        except InvalidTokenError as exc:
            _log.info("token rejected", extra={"error_type": type(exc).__name__})
            raise TokenRejectedError(f"{type(exc).__name__}: {exc}") from exc

        groups = claims.get("groups") or []
        if not isinstance(groups, list):
            groups = []

        return TokenClaims(
            subject=str(claims["sub"]),
            email=claims.get("email"),
            name=claims.get("name") or claims.get("preferred_username"),
            groups=tuple(str(g) for g in groups),
            raw=claims,
        )
