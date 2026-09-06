"""Service Account API keys (FR-389).

> Keys are prefix-identifiable, **hashed at rest, never retrievable after creation**.
> They carry an expiry, are rotatable with an overlap window, and are scoped to named
> environments and the scoring permission set only.

Key format::

    gip_{environment}_{prefix}_{secret}
    gip_prod_7f2a1c9d_9b1e…                (the whole string is the credential)

No field contains an underscore, so the format is unambiguous however it is split.

The **prefix is stored in clear** and the secret is not. That is what makes a leaked key
actionable: a key found in a log or a repository can be identified and revoked from its
prefix alone, without anyone ever holding the secret. It is also what makes lookup a single
indexed query rather than a scan comparing hashes.

**Why SHA-256 rather than Argon2.** A slow KDF exists to make guessing a *low-entropy*
secret expensive. These secrets are 256 bits from `secrets.token_urlsafe` — guessing is
infeasible by construction, so stretching adds latency to every scoring request and buys
nothing. The threat model is database disclosure, and SHA-256 of 256 random bits is not
invertible. A user password would need Argon2; this is not one, and the platform stores no
passwords at all (FR-387).
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from typing import Final, NamedTuple

__all__ = [
    "KEY_PREFIX_LENGTH",
    "GeneratedKey",
    "generate_key",
    "hash_secret",
    "parse_key",
    "verify_secret",
]

_NAMESPACE: Final = "gip"
KEY_PREFIX_LENGTH: Final = 8
_SECRET_BYTES: Final = 32  # 256 bits


class ParsedKey(NamedTuple):
    """The parts of a presented key. `secret` is never persisted anywhere."""

    environment: str
    prefix: str
    secret: str


class GeneratedKey(NamedTuple):
    """A freshly minted key.

    `value` is returned to the caller exactly once and then discarded — nothing stores it,
    which is why the API cannot show it again and must say so plainly at creation.
    """

    value: str
    prefix: str
    secret_hash: str
    environment: str


def generate_key(environment: str) -> GeneratedKey:
    """Mint a key for an environment."""
    if not environment or "_" in environment:
        raise ValueError(
            f"environment {environment!r} must be non-empty and contain no underscore: "
            "the underscore separates the fields of a key"
        )
    prefix = secrets.token_hex(KEY_PREFIX_LENGTH // 2)
    # Hex, not `token_urlsafe`: the urlsafe alphabet includes `_`, which is the character
    # separating the fields of a key. `parse_key` handles it correctly with `maxsplit=3`,
    # but a format whose separator can appear inside a field invites the `rsplit` mistake
    # from anyone reading a key — and it did, in this repo, within an hour of the format
    # being written. 32 bytes of hex is still 256 bits.
    secret = secrets.token_hex(_SECRET_BYTES)
    return GeneratedKey(
        value=f"{_NAMESPACE}_{environment}_{prefix}_{secret}",
        prefix=prefix,
        secret_hash=hash_secret(secret),
        environment=environment,
    )


def parse_key(value: str) -> ParsedKey | None:
    """Split a presented key, or `None` when it is not one of ours.

    Returning `None` rather than raising: a malformed key and a wrong key must be
    indistinguishable to the caller, so both produce the same `API_KEY_INVALID`.
    """
    parts = value.split("_", 3)
    if len(parts) != 4:
        return None
    namespace, environment, prefix, secret = parts
    if namespace != _NAMESPACE or not environment or not secret:
        return None
    if len(prefix) != KEY_PREFIX_LENGTH:
        return None
    return ParsedKey(environment=environment, prefix=prefix, secret=secret)


def hash_secret(secret: str) -> str:
    return "sha256:" + hashlib.sha256(secret.encode()).hexdigest()


def verify_secret(secret: str, stored_hash: str) -> bool:
    """Constant-time comparison.

    `==` on digests leaks their prefix through timing. The window is small and the secret
    is long, but the fix is one function call and the reasoning to skip it is longer than
    the code.
    """
    return hmac.compare_digest(hash_secret(secret), stored_hash)
