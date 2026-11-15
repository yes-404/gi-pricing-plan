"""`AuditEventRecord`: an audit event plus its chain position (`06` §4.5, FR-372)."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from model_schema import (
    ActorKind,
    AuditEvent,
    AuditEventCore,
    AuditEventRecord,
    JobSource,
    Principal,
    compute_event_hash,
    new_uuid7,
)


def _record(sequence: int = 1) -> AuditEventRecord:
    core = AuditEventCore(
        id=new_uuid7(),
        workspace_id=new_uuid7(),
        at=datetime(2026, 11, 14, 9, 0, tzinfo=UTC),
        actor=Principal(kind=ActorKind.USER, id=new_uuid7(), display="a.actuary"),
        source=JobSource.API,
        action="model.submitted",
        entity_ref="model:motor@1",
    )
    return AuditEventRecord(
        **core.model_dump(),
        sequence=sequence,
        prev_event_hash=None,
        event_hash=compute_event_hash(core, prev_event_hash=None),
    )


@pytest.mark.req("FR-372")
def test_a_record_verifies_and_the_sequence_is_not_hashed() -> None:
    record = _record(sequence=1)
    assert record.verify()
    moved = record.model_copy(update={"sequence": 99})
    assert moved.verify()  # the position is not part of the hashed content


@pytest.mark.req("FR-372")
def test_a_record_round_trips_through_json_lines_and_still_verifies() -> None:
    record = _record()
    assert AuditEventRecord.model_validate_json(record.model_dump_json()).verify()


@pytest.mark.req("FR-372")
def test_an_edited_record_fails_to_verify() -> None:
    edited = _record().model_copy(update={"justification": "edited"})
    assert not edited.verify()


@pytest.mark.req("FR-372")
def test_a_record_needs_a_sequence_from_one() -> None:
    with pytest.raises(ValidationError):
        AuditEventRecord.model_validate({**_record().model_dump(mode="json"), "sequence": 0})
    with pytest.raises(ValidationError):
        AuditEvent.model_validate(_record().model_dump(mode="json"))  # extra=forbid: no sequence
