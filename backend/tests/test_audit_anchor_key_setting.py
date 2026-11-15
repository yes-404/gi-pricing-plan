"""`GIP_AUDIT_ANCHOR_SIGNING_KEY` (`06` FR-373 (2)): a set key must load, and never leaks.

Test keys are generated here, at test time. No key literal is committed.
"""

from __future__ import annotations

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from pydantic import SecretStr

from app.config import ConfigInvalidError, Settings, load_anchor_signing_key, load_settings


def _pem(key: Ed25519PrivateKey | rsa.RSAPrivateKey) -> str:
    return key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()


@pytest.mark.req("FR-373")
def test_the_key_is_optional() -> None:
    assert load_settings().audit_anchor_signing_key is None


@pytest.mark.req("FR-373")
def test_a_valid_ed25519_key_loads() -> None:
    key = Ed25519PrivateKey.generate()
    settings = load_settings(audit_anchor_signing_key=_pem(key))
    assert settings.audit_anchor_signing_key is not None
    loaded = load_anchor_signing_key(settings.audit_anchor_signing_key)
    assert loaded.public_key().public_bytes_raw() == key.public_key().public_bytes_raw()


@pytest.mark.req("FR-373")
def test_a_malformed_key_refuses_start_up() -> None:
    with pytest.raises(ConfigInvalidError, match="GIP_AUDIT_ANCHOR_SIGNING_KEY"):
        load_settings(audit_anchor_signing_key="not a key")


@pytest.mark.req("FR-373")
def test_a_key_of_another_algorithm_refuses_start_up() -> None:
    rsa_pem = _pem(rsa.generate_private_key(public_exponent=65537, key_size=2048))
    with pytest.raises(ConfigInvalidError, match="Ed25519"):
        load_settings(audit_anchor_signing_key=rsa_pem)


@pytest.mark.req("FR-373")
def test_neither_the_error_nor_the_repr_carries_the_key() -> None:
    body = "".join(_pem(Ed25519PrivateKey.generate()).splitlines()[1:-1])
    with pytest.raises(ConfigInvalidError) as refused:
        load_settings(audit_anchor_signing_key=f"-----BEGIN PRIVATE KEY-----\n{body}A\n")
    assert body not in str(refused.value)
    assert refused.value.__cause__ is None

    settings = Settings(audit_anchor_signing_key=SecretStr(_pem(Ed25519PrivateKey.generate())))
    assert settings.audit_anchor_signing_key is not None
    secret = settings.audit_anchor_signing_key.get_secret_value()
    marker = secret.splitlines()[1]
    assert marker not in repr(settings)
    assert marker not in str(settings.model_dump())
    assert marker not in settings.model_dump_json()
