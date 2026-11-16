"""The anchor's shape and its signed bytes (`06` FR-373 (1), (6)).

The customer rebuilds these bytes with `json.dumps` and the arguments FR-373 (6) names, so a
change to them breaks every stored anchor: the fixture below is pinned.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from model_schema import AnchorStatement, AuditAnchor, anchor_statement_bytes

_HASH = "sha256:" + "ab" * 32
_KEY = "sha256:" + "cd" * 32


def _statement(**changes: object) -> AnchorStatement:
    fields: dict[str, object] = {
        "workspace_id": UUID("0190b5a2-7c3e-7a10-9d21-4f6b8c2e1a01"),
        "head_sequence": 7,
        "head_event_hash": _HASH,
        "anchored_at": datetime(2026, 11, 15, 10, 11, 0, 482000, tzinfo=UTC),
        "key_id": _KEY,
        **changes,
    }
    return AnchorStatement.model_validate(fields)


@pytest.mark.req("FR-373")
def test_the_signed_bytes_are_pinned() -> None:
    expected = (
        '{"anchor_version":1,'
        '"anchored_at":"2026-11-15T10:11:00.482000Z",'
        f'"head_event_hash":"{_HASH}",'
        '"head_sequence":7,'
        f'"key_id":"{_KEY}",'
        '"previous_key_id":null,'
        '"workspace_id":"0190b5a2-7c3e-7a10-9d21-4f6b8c2e1a01"}'
    ).encode()
    assert anchor_statement_bytes(_statement()) == expected


@pytest.mark.req("FR-373")
def test_the_customer_rule_rebuilds_the_same_bytes() -> None:
    statement = _statement(previous_key_id=_KEY)
    wire = json.loads(statement.model_dump_json())
    rebuilt = json.dumps(wire, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    assert rebuilt.encode() == anchor_statement_bytes(statement)


@pytest.mark.req("FR-373")
def test_an_empty_chain_is_sequence_zero_with_no_hash() -> None:
    assert _statement(head_sequence=0, head_event_hash=None).head_sequence == 0
    with pytest.raises(ValidationError):
        _statement(head_sequence=0)
    with pytest.raises(ValidationError):
        _statement(head_event_hash=None)


@pytest.mark.req("FR-373")
def test_a_naive_timestamp_is_refused() -> None:
    with pytest.raises(ValidationError):
        _statement(anchored_at=datetime(2026, 11, 15, 10, 11))


@pytest.mark.req("FR-373")
def test_the_anchor_carries_the_statement_and_forbids_extras() -> None:
    anchor = AuditAnchor(statement=_statement(), public_key="a", signature="b")
    assert anchor.algorithm == "Ed25519"
    with pytest.raises(ValidationError):
        AuditAnchor.model_validate({**anchor.model_dump(mode="json"), "extra": 1})
