"""OIDC token verification (FR-387).

Tokens are signed with a real RSA key and verified through a real JWKS served over HTTP,
so the fetch-and-verify path runs as it does in production. Monkeypatching the key lookup
would skip exactly the part that decides whether a forged token is accepted.
"""

from __future__ import annotations

import http.server
import json
import threading
import time
from collections.abc import Iterator

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from app.auth.oidc import ALLOWED_ALGORITHMS, OidcVerifier, TokenRejectedError
from app.config import Settings

ISSUER = "https://idp.test.example/realms/gip"
AUDIENCE = "gi-pricing-api"
KID = "test-key-1"


@pytest.fixture(scope="module")
def rsa_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture(scope="module")
def jwks_server(rsa_key: rsa.RSAPrivateKey) -> Iterator[str]:
    """Serve a JWKS containing the public half of `rsa_key`."""
    public_jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(rsa_key.public_key()))
    public_jwk.update({"kid": KID, "use": "sig", "alg": "RS256"})
    body = json.dumps({"keys": [public_jwk]}).encode()

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args: object) -> None:
            return

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}/jwks.json"
    server.shutdown()


@pytest.fixture
def settings(jwks_server: str) -> Settings:
    return Settings(
        oidc_issuer=ISSUER, oidc_audience=AUDIENCE, oidc_jwks_url=jwks_server
    )


@pytest.fixture
def verifier(settings: Settings) -> OidcVerifier:
    return OidcVerifier(settings)


def _token(key: rsa.RSAPrivateKey, **overrides: object) -> str:
    now = int(time.time())
    claims: dict[str, object] = {
        "iss": ISSUER,
        "aud": AUDIENCE,
        "sub": "user-123",
        "iat": now,
        "exp": now + 300,
        "email": "a.actuary@insurer.example",
        "name": "A Actuary",
        "groups": ["pricing", "reviewers"],
    }
    claims.update(overrides)
    return jwt.encode(claims, key, algorithm="RS256", headers={"kid": KID})


@pytest.mark.req("FR-387")
def test_a_valid_token_yields_its_claims(verifier: OidcVerifier, rsa_key) -> None:
    claims = verifier.verify(_token(rsa_key))
    assert claims.subject == "user-123"
    assert claims.email == "a.actuary@insurer.example"
    assert claims.groups == ("pricing", "reviewers")


@pytest.mark.req("FR-388")
def test_an_expired_token_is_refused(verifier: OidcVerifier, rsa_key) -> None:
    """Short-lived tokens are only short-lived if expiry is enforced with no leeway."""
    past = int(time.time()) - 10
    with pytest.raises(TokenRejectedError):
        verifier.verify(_token(rsa_key, exp=past, iat=past - 300))


@pytest.mark.req("FR-387")
def test_a_token_for_another_audience_is_refused(verifier: OidcVerifier, rsa_key) -> None:
    """Negative: the same provider issues tokens for other clients. They are not ours."""
    with pytest.raises(TokenRejectedError):
        verifier.verify(_token(rsa_key, aud="some-other-client"))


@pytest.mark.req("FR-387")
def test_a_token_from_another_issuer_is_refused(verifier: OidcVerifier, rsa_key) -> None:
    with pytest.raises(TokenRejectedError):
        verifier.verify(_token(rsa_key, iss="https://evil.example/realms/gip"))


@pytest.mark.req("FR-387")
def test_algorithm_confusion_is_refused(verifier: OidcVerifier, rsa_key) -> None:
    """The attack this allow-list exists for.

    An HS256 token whose HMAC secret is the provider's *public* key verifies against a
    naive implementation, because the public key is not secret — anyone who can read the
    JWKS could mint tokens for any user.

    The token is assembled by hand rather than with `jwt.encode`, which refuses to sign
    HS256 with a PEM public key. That guard protects the *signer*; an attacker is not
    using PyJWT, so testing through it would prove nothing about the verifier.
    """
    import base64
    import hashlib
    import hmac

    from cryptography.hazmat.primitives import serialization

    public_pem = rsa_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    def b64(raw: bytes) -> bytes:
        return base64.urlsafe_b64encode(raw).rstrip(b"=")

    now = int(time.time())
    header = b64(json.dumps({"alg": "HS256", "typ": "JWT", "kid": KID}).encode())
    payload = b64(
        json.dumps(
            {"iss": ISSUER, "aud": AUDIENCE, "sub": "attacker", "iat": now, "exp": now + 300}
        ).encode()
    )
    signing_input = header + b"." + payload
    signature = b64(hmac.new(public_pem, signing_input, hashlib.sha256).digest())
    forged = (signing_input + b"." + signature).decode()

    with pytest.raises(TokenRejectedError):
        verifier.verify(forged)
    assert "HS256" not in ALLOWED_ALGORITHMS
    assert "none" not in ALLOWED_ALGORITHMS


@pytest.mark.req("FR-387")
def test_an_unsigned_token_is_refused(verifier: OidcVerifier, rsa_key) -> None:
    now = int(time.time())
    unsigned = jwt.encode(
        {"iss": ISSUER, "aud": AUDIENCE, "sub": "attacker", "iat": now, "exp": now + 300},
        key="",
        algorithm="none",
        headers={"kid": KID},
    )
    with pytest.raises(TokenRejectedError):
        verifier.verify(unsigned)


@pytest.mark.req("FR-387")
def test_a_token_signed_by_another_key_is_refused(verifier: OidcVerifier) -> None:
    """Negative: a correctly-shaped token from a key the provider never published."""
    attacker_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    with pytest.raises(TokenRejectedError):
        verifier.verify(_token(attacker_key))


@pytest.mark.req("FR-387")
def test_a_token_without_a_subject_is_refused(verifier: OidcVerifier, rsa_key) -> None:
    """`sub` is the user's identity; without it there is nobody to authenticate as."""
    now = int(time.time())
    token = jwt.encode(
        {"iss": ISSUER, "aud": AUDIENCE, "iat": now, "exp": now + 300},
        rsa_key,
        algorithm="RS256",
        headers={"kid": KID},
    )
    with pytest.raises(TokenRejectedError):
        verifier.verify(token)


@pytest.mark.req("FR-387")
def test_verification_is_refused_when_no_provider_is_configured(rsa_key) -> None:
    """Negative: an unconfigured platform must reject tokens, not accept them unverified."""
    verifier = OidcVerifier(Settings())
    with pytest.raises(TokenRejectedError, match="no identity provider"):
        verifier.verify(_token(rsa_key))


@pytest.mark.req("NFR-532")
def test_rejection_reasons_are_not_returned_to_the_caller(
    verifier: OidcVerifier, rsa_key
) -> None:
    """The reason is logged, never surfaced — it tells an attacker what to fix next."""
    from app.auth.service import _unauthenticated

    problem = _unauthenticated().to_problem()
    assert "signature" not in (problem.detail or "").lower()
    assert "expired" not in (problem.detail or "").lower()
