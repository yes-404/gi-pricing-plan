"""Service Account API keys (FR-PLAT-3, FR-PLAT-6, FR-PLAT-30)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select

from app.auth.api_keys import KEY_PREFIX_LENGTH, generate_key, hash_secret, parse_key, verify_secret
from app.auth.service import authenticate_api_key
from app.db.models import ApiKeyRow, AuditEventRow, ServiceAccountRow
from app.db.session import Database
from app.errors import PlatformError
from model_schema import ActorKind, new_uuid7

# -- key primitives ------------------------------------------------------------------------


@pytest.mark.req("FR-PLAT-3")
def test_a_key_is_prefix_identifiable() -> None:
    """A key found in a log must be identifiable and revocable without holding the secret."""
    generated = generate_key("prod")
    parsed = parse_key(generated.value)
    assert parsed is not None
    assert parsed.prefix == generated.prefix
    assert parsed.environment == "prod"
    assert len(generated.prefix) == KEY_PREFIX_LENGTH
    assert generated.value.startswith(f"gip_prod_{generated.prefix}_")


@pytest.mark.req("FR-PLAT-3")
def test_the_secret_is_never_stored_only_its_hash() -> None:
    generated = generate_key("prod")
    parsed = parse_key(generated.value)
    assert parsed is not None
    secret = parsed.secret
    assert generated.secret_hash.startswith("sha256:")
    assert secret not in generated.secret_hash
    assert verify_secret(secret, generated.secret_hash)


@pytest.mark.req("FR-PLAT-3")
def test_a_wrong_secret_does_not_verify() -> None:
    generated = generate_key("prod")
    assert not verify_secret("not-the-secret", generated.secret_hash)


@pytest.mark.req("FR-PLAT-3")
def test_keys_are_unique() -> None:
    assert len({generate_key("prod").value for _ in range(200)}) == 200


@pytest.mark.req("FR-PLAT-3")
@pytest.mark.parametrize(
    "value",
    ["", "gip", "gip_prod", "gip_prod_short_secret", "notgip_prod_7f2a1c9d_secret", "random"],
)
def test_a_malformed_key_is_not_parsed(value: str) -> None:
    """Negative: a malformed key and a wrong key must be indistinguishable to the caller."""
    assert parse_key(value) is None


@pytest.mark.req("FR-PLAT-3")
def test_an_environment_with_an_underscore_is_refused() -> None:
    """The underscore separates key fields; allowing one would make parsing ambiguous."""
    with pytest.raises(ValueError, match="underscore"):
        generate_key("pre_prod")


# -- authentication ------------------------------------------------------------------------


async def _account_with_key(
    database: Database,
    workspace_id,
    *,
    environments: list[str] | None = None,
    expires_in_days: int = 365,
    revoked: bool = False,
):
    async with database.unit_of_work() as session:
        account = ServiceAccountRow(
            workspace_id=workspace_id,
            slug=f"acct-{new_uuid7().hex[-12:]}",
            environments=environments or ["prod"],
            permissions=["score:execute"],
        )
        session.add(account)
        await session.flush()
        generated = generate_key((environments or ["prod"])[0])
        key = ApiKeyRow(
            service_account_id=account.id,
            prefix=generated.prefix,
            secret_hash=generated.secret_hash,
            environment=generated.environment,
            expires_at=datetime.now(UTC) + timedelta(days=expires_in_days),
            revoked_at=datetime.now(UTC) if revoked else None,
        )
        session.add(key)
        await session.flush()
        return account.id, generated.value


@pytest.mark.req("FR-PLAT-3")
async def test_a_valid_key_authenticates_as_the_service_account(
    database: Database, workspace_id
) -> None:
    account_id, value = await _account_with_key(database, workspace_id)
    async with database.unit_of_work() as session:
        identity = await authenticate_api_key(session, value)
    assert identity.principal.kind is ActorKind.SERVICE_ACCOUNT
    assert identity.principal.id == account_id
    assert identity.workspaces == frozenset({workspace_id})
    assert identity.permissions == frozenset({"score:execute"})


@pytest.mark.req("FR-PLAT-3")
async def test_using_a_key_records_when(database: Database, workspace_id) -> None:
    _, value = await _account_with_key(database, workspace_id)
    async with database.unit_of_work() as session:
        await authenticate_api_key(session, value)

    prefix = parse_key(value).prefix  # type: ignore[union-attr]
    async with database.session() as session:
        key = (
            await session.execute(select(ApiKeyRow).where(ApiKeyRow.prefix == prefix))
        ).scalar_one()
    assert key.last_used_at is not None


@pytest.mark.req("FR-PLAT-3")
async def test_an_expired_key_is_refused(database: Database, workspace_id) -> None:
    _, value = await _account_with_key(database, workspace_id, expires_in_days=-1)
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await authenticate_api_key(session, value)
    assert exc.value.code == "API_KEY_EXPIRED"
    assert exc.value.status_code == 401


@pytest.mark.req("FR-PLAT-3")
async def test_a_revoked_key_is_refused(database: Database, workspace_id) -> None:
    _, value = await _account_with_key(database, workspace_id, revoked=True)
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await authenticate_api_key(session, value)
    assert exc.value.code == "API_KEY_INVALID"


@pytest.mark.req("FR-PLAT-30")
async def test_the_environment_in_the_key_is_a_label_not_an_authorisation(
    database: Database, workspace_id
) -> None:
    """FR-PLAT-30: a uat key can never score against prod.

    The hash covers the **secret only**, so an attacker can rewrite the environment field
    of a key they legitimately hold and it still verifies. The grant on the account is
    what decides — this asserts the exact code, because accepting either would not
    distinguish "the environment check fired" from "the tampering broke the secret".
    """
    _, value = await _account_with_key(database, workspace_id, environments=["uat"])
    forged = value.replace("gip_uat_", "gip_prod_", 1)
    assert forged != value

    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError) as exc:
            await authenticate_api_key(session, forged)
    assert exc.value.code == "ENVIRONMENT_SCOPE_DENIED"

    # The unmodified key still works — proving the rejection was the environment grant and
    # not a side effect of touching the string.
    async with database.unit_of_work() as session:
        identity = await authenticate_api_key(session, value)
    assert identity.environments == frozenset({"uat"})


@pytest.mark.req("FR-PLAT-3")
async def test_an_unknown_prefix_and_a_wrong_secret_fail_identically(
    database: Database, workspace_id
) -> None:
    """Negative: distinguishing them turns the prefix into an oracle for which keys exist."""
    _, value = await _account_with_key(database, workspace_id)
    parsed = parse_key(value)
    assert parsed is not None
    wrong_secret = f"gip_{parsed.environment}_{parsed.prefix}_" + "x" * 64
    unknown_prefix = generate_key("prod").value

    codes = set()
    for candidate in (wrong_secret, unknown_prefix):
        async with database.unit_of_work() as session:
            with pytest.raises(PlatformError) as exc:
                await authenticate_api_key(session, candidate)
        codes.add((exc.value.code, exc.value.status_code, exc.value.detail))
    assert len(codes) == 1


@pytest.mark.req("FR-PLAT-6")
async def test_a_failed_authentication_is_audited(database: Database, workspace_id) -> None:
    _, value = await _account_with_key(database, workspace_id, revoked=True)
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError):
            await authenticate_api_key(session, value)

    async with database.session() as session:
        events = (
            await session.execute(
                select(AuditEventRow).where(AuditEventRow.workspace_id == workspace_id)
            )
        ).scalars().all()
    assert [e.action for e in events] == ["principal.auth_failed"]
    assert events[0].after["reason"] == "key revoked"


@pytest.mark.req("NFR-PLAT-7")
async def test_no_audit_event_contains_a_key_secret(
    database: Database, workspace_id
) -> None:
    """R3 / FR-PLAT-27: keys are audited by prefix. An audit log holding secrets is a
    credential store with a retention policy."""
    _, value = await _account_with_key(database, workspace_id, revoked=True)
    secret = parse_key(value).secret  # type: ignore[union-attr]
    async with database.unit_of_work() as session:
        with pytest.raises(PlatformError):
            await authenticate_api_key(session, value)

    async with database.session() as session:
        events = (
            await session.execute(
                select(AuditEventRow).where(AuditEventRow.workspace_id == workspace_id)
            )
        ).scalars().all()
    for event in events:
        assert secret not in str(event.after)
        assert secret not in str(event.before)


@pytest.mark.req("FR-PLAT-3")
def test_hashing_is_stable() -> None:
    assert hash_secret("abc") == hash_secret("abc")
    assert hash_secret("abc") != hash_secret("abd")
