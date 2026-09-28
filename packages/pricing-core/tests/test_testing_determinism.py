"""`generate_contexts` — the seed, the settings and the version (03 §5.2, FR-261; PL-1205 Task 3).

RS-1176's conditions 2, 3 and 6: the generation settings are fixed and asserted, a generator
built against another `hypothesis` version is refused by name, and two fresh interpreters
given the same persisted seed produce byte-identical case logs.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import textwrap
from typing import Any

import hypothesis
import pytest

from model_schema.rating import InputContractField
from model_schema.scoring import QuoteContext
from pricing_core.rating.testing import GeneratorVersionMismatch, generate_contexts

_CONTRACT = [
    InputContractField.model_validate(f)
    for f in (
        {"name": "driver_age", "type": "int", "min": 17, "max": 99},
        {"name": "channel", "type": "enum", "domain": ["direct", "broker"]},
        {"name": "ncd_years", "type": "int", "min": 0, "max": 9, "nullable": True},
        {"name": "vehicle_value", "type": "decimal", "min": 500, "max": 90000},
        {"name": "postcode", "type": "string", "pattern": "[A-Z]{1,2}[0-9]{1,2}"},
        {"name": "start", "type": "date"},
        {"name": "telematics", "type": "bool"},
    )
]


def _canonical(contexts: list[QuoteContext]) -> str:
    payload = [c.model_dump(mode="json") for c in contexts]
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


@pytest.mark.req("FR-261")
def test_the_same_seed_gives_the_same_cases_in_process() -> None:
    one = generate_contexts(_CONTRACT, 30, 11)
    two = generate_contexts(_CONTRACT, 30, 11)
    assert _canonical(one) == _canonical(two)
    assert len(one) == 30
    assert _canonical(generate_contexts(_CONTRACT, 30, 12)) != _canonical(one)


@pytest.mark.req("FR-261")
def test_every_case_satisfies_the_input_contract() -> None:
    for ctx in generate_contexts(_CONTRACT, 40, 3):
        i = ctx.inputs
        assert 17 <= i["driver_age"] <= 99  # type: ignore[operator]
        assert i["channel"] in {"direct", "broker"}
        assert i["ncd_years"] is None or 0 <= i["ncd_years"] <= 9  # type: ignore[operator]
        assert not isinstance(i["vehicle_value"], float)
        assert isinstance(i["telematics"], bool)


@pytest.mark.req("FR-261")
def test_the_generation_settings_are_the_declared_ones() -> None:
    """RS-1176 condition 2: what `run_regression` and `generate_contexts` both apply."""
    from pricing_core.rating.testing import generation_settings

    s = generation_settings(123)
    assert s.database is None
    assert s.deadline is None
    assert s.report_multiple_bugs is False
    assert s.derandomize is False
    assert s.max_examples == 123
    assert s.suppress_health_check == ()  # PL-1205:311's list, nothing added


@pytest.mark.req("FR-261")
def test_a_version_mismatch_is_refused_naming_both_versions() -> None:
    with pytest.raises(GeneratorVersionMismatch) as caught:
        generate_contexts(_CONTRACT, 5, 1, expect_version="0.0.1")
    assert "0.0.1" in str(caught.value)
    assert hypothesis.__version__ in str(caught.value)
    assert isinstance(caught.value, ValueError)
    assert len(generate_contexts(_CONTRACT, 5, 1, expect_version=hypothesis.__version__)) == 5


_CHILD = textwrap.dedent(
    """
    import hashlib, json, sys
    from model_schema.rating import InputContractField
    from pricing_core.rating import testing

    contract = [InputContractField.model_validate(f) for f in json.loads(sys.argv[2])]
    seed = None if sys.argv[1] == "none" else int(sys.argv[1])
    ctxs = testing._draw_contexts(contract, 30, seed)
    payload = [c.model_dump(mode="json") for c in ctxs]
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    print(hashlib.sha256(blob).hexdigest())
    """
)


def _child(seed: str, hashseed: str) -> str:
    fields: list[dict[str, Any]] = [f.model_dump(mode="json") for f in _CONTRACT]
    out = subprocess.run(
        [sys.executable, "-c", _CHILD, seed, json.dumps(fields)],
        check=True, capture_output=True, text=True,
        env={**os.environ, "PYTHONHASHSEED": hashseed},
    )
    return out.stdout.strip()


@pytest.mark.req("FR-261")
def test_the_same_seed_gives_the_same_cases_across_fresh_interpreters() -> None:
    """RS-1176 condition 6, positive: different hash seeds, one persisted seed."""
    assert _child("424242", "1") == _child("424242", "2")


@pytest.mark.req("FR-261")
def test_the_comparator_can_fail_without_a_persisted_seed() -> None:
    """RS-1176 condition 6, negative control: no seed, and the logs differ."""
    assert _child("none", "1") != _child("none", "1")
