"""R5 (PL-1710): the WF-701 failure line names the missing replica and counts the extras (FR-268).

DB-free: the line is built from the failure's journey-computed fields, never from its `detail`,
which can carry server text (the extra process ids, the stray bundle hashes).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "examples" / "fremtpl2"))
import journey_wf701 as j  # noqa: E402

_SPEC = importlib.util.spec_from_file_location("demo_script", _ROOT / "scripts" / "demo.py")
assert _SPEC is not None
assert _SPEC.loader is not None
demo_script = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(demo_script)


@pytest.mark.req("FR-268")
def test_the_commit_set_failure_line_names_the_missing_replicas_and_counts_the_extra() -> None:
    processes = {"host-a:1:1": "committed", "host-x:2:2": "committed"}
    with pytest.raises(j.JourneyStepFailed) as failure:
        j.check_commit_set("A2", processes, frozenset({"host-a", "host-b", "host-c"}))
    line = demo_script.journey_failure_line(failure.value, "wf-701")
    assert "COMMIT_SET_DIFFERS_FROM_THE_REPLICAS" in line
    assert "host-b" in line
    assert "host-c" in line
    assert "+1 extra" in line
    assert "host-x" not in line  # the extra set is server-reported: a count, never its text


@pytest.mark.req("FR-268")
def test_the_bundle_hash_failure_line_prints_the_journey_hashes_and_counts_the_strays() -> None:
    old, new = "sha256:" + "a" * 64, "sha256:" + "b" * 64
    stray = "sha256:" + "c" * 64
    with pytest.raises(j.JourneyStepFailed) as failure:
        j.check_old_or_new("A2", [old, stray, new], old, new)
    line = demo_script.journey_failure_line(failure.value, "wf-701")
    assert "BUNDLE_HASH_NEITHER_OLD_NOR_NEW" in line
    assert old in line
    assert new in line
    assert "+1 extra" in line
    assert stray not in line


@pytest.mark.req("FR-268")
def test_a_failure_without_names_keeps_the_code_and_status_line() -> None:
    class Plain:
        step, code, status = "C1", "VALIDATION_FAILED", 422

    assert (
        demo_script.journey_failure_line(Plain())
        == "the WF-699 journey failed at C1: VALIDATION_FAILED (HTTP 422)"
    )
