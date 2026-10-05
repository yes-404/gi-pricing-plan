"""The Premium Ladder's contract shape (`RL-1329` §3, Acceptance 5)."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

from model_schema.scoring import LadderOperation, LadderRung, ScoringResult

_REPO = Path(__file__).resolve().parents[3]
_SCHEMA = _REPO / "docs" / "contracts" / "schemas" / "scoring.schema.json"

_REF = {"type": "rating_version", "slug": "motor", "version": 1}


def _result(rungs: list[dict[str, object]]) -> dict[str, object]:
    return {
        "outcome": "quoted", "rating_version_ref": _REF, "bundle_hash": "sha256:" + "0" * 64,
        "premium_ladder": rungs, "outputs": {},
    }


@pytest.mark.req("FR-248")
def test_a_new_result_carries_unrounded_value_and_rounding_on_every_rung() -> None:
    result = ScoringResult.model_validate(_result([
        {"rung": "risk_premium", "value_minor": 61234, "unrounded_minor": "61234.5",
         "rounding": {"mode": "half_even", "dp": 0}},
        {"rung": "office_premium", "value_minor": 67358, "unrounded_minor": "67357.95",
         "rounding": {"mode": "half_even", "dp": 0},
         "operation": {"kind": "multiply", "factor": "1.1"}},
        {"rung": "constraints", "value_minor": 67358, "unrounded_minor": "67357.95",
         "rounding": {"mode": "half_even", "dp": 0},
         "operation": {"kind": "clamp", "bound": "min", "bound_unrounded_minor": "5000",
                       "applied": ["MIN_PREMIUM_APPLIED"]}},
    ]))
    dumped = json.loads(result.model_dump_json())["premium_ladder"]
    assert dumped[1]["unrounded_minor"] == "67357.95"
    assert dumped[1]["operation"]["factor"] == "1.1"  # never quantised to "1.1000"
    assert dumped[2]["operation"]["bound_unrounded_minor"] == "5000"


@pytest.mark.req("FR-248")
def test_a_stored_pre_ruling_ladder_still_validates() -> None:
    """Stored ladders are write-once and lack every `RL-1329` field, including the legacy
    `amount_minor` and a four-dp `factor`."""
    stored = ScoringResult.model_validate(_result([
        {"rung": "risk_premium", "value_minor": 24150},
        {"rung": "expense_loading", "value_minor": 27772,
         "operation": {"kind": "multiply", "factor": "1.1500", "mode": "half_even", "dp": 0}},
        {"rung": "ipt_and_fees", "value_minor": 31612,
         "operation": {"kind": "add", "amount_minor": 3840}},
    ]))
    assert stored.premium_ladder[0].unrounded_minor is None
    assert stored.premium_ladder[1].operation is not None
    assert stored.premium_ladder[1].operation.factor == Decimal("1.1500")
    assert stored.premium_ladder[2].operation is not None
    assert stored.premium_ladder[2].operation.amount_minor == 3840


@pytest.mark.req("FR-248")
def test_the_hand_authored_contract_declares_every_model_field() -> None:
    """The hand-authored `scoring.schema.json` and the models change together (ADR-704)."""
    defs = json.loads(_SCHEMA.read_text())["$defs"]
    rung = defs["LadderRung"]["properties"]
    assert set(LadderRung.model_fields) <= set(rung)
    operation = rung["operation"]["properties"]
    assert set(LadderOperation.model_fields) == set(operation)
    assert set(operation["kind"]["enum"]) == {
        "multiply", "divide", "add", "clamp", "round", "none",
    }
    for decimal_field in ("factor", "divisor", "amount_unrounded_minor", "bound_unrounded_minor"):
        assert operation[decimal_field] == {"$ref": "common/money.schema.json#/$defs/Decimal"}
    assert rung["unrounded_minor"] == {"$ref": "common/money.schema.json#/$defs/Decimal"}
    assert rung["rounding"] == {"$ref": "common/money.schema.json#/$defs/Rounding"}


@pytest.mark.req("FR-248")
def test_a_trace_carries_an_optional_ladder_check_version() -> None:
    """`PL-1342` Acceptance 10: absent or 1 means the pre-ruling shallow check, 2 the full one."""
    from model_schema.scoring import Trace

    base: dict[str, object] = {
        "rating_version_ref": _REF, "bundle_hash": "sha256:" + "0" * 64,
        "steps": [], "ladder_reconciled": True,
    }
    assert Trace.model_validate(base).ladder_check_version is None  # a stored trace
    assert Trace.model_validate({**base, "ladder_check_version": 2}).ladder_check_version == 2
    trace_def = json.loads(_SCHEMA.read_text())["$defs"]["Trace"]
    assert set(Trace.model_fields) <= set(trace_def["properties"])
    assert "ladder_check_version" not in trace_def["required"]
