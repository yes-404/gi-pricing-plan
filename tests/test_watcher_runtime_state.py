"""`.claude/skills/watcher-runtime-state/scripts/write_runtime_state.py` -- the NT-0014
runtime state file (artifact B), rebuilt to Ruling 47's shape
(`docs/plans/2026-08-30-nt-0014-q1-q3-q4-rulings.md`).

Ruling 47 rejected the note's original design -- a state file the watcher writes and a
mismatch detector compares against artifact history -- because that design's actual
failure mode is agreement by vacancy: a dead or unwired writer leaves both sides reading
zero, so the mismatch never fires. The ruling requires the watcher to **re-derive**
rather than compare, and binds the result with four falsifiability conditions: no
file-level freshness token, `retry_counters` absent entirely until C2 exists,
`in_flight_expensive_verifications` entries carry a TTL and expire, and position fields
name the artifact they were read from. Ruling 47(d) states the acceptance test as the
violation that must become impossible: **a cycle in which nothing changed must produce a
byte-identical file.** This module tests that, plus each of the three conditions above
that a mechanical check can express (the fourth -- position fields naming their source
-- is exercised by `test_position_fields_carry_their_source`).

No `@pytest.mark.req` marker: this is correctness of a process-mechanism script, not
evidence for a numbered platform requirement, the same posture `tests/
test_scope_audit.py` takes for `scripts/scope-audit.py`. Every case runs the script as a
real subprocess against a `tmp_path`-scoped `RUNTIME_STATE_FILE`, never against the real
`~/gi-pricing-plan.local/handover/runtime-state.json` -- this repository's rule that
runtime/ops state lives outside the repository (`docs/process/delivery-process.md` §10)
cuts both ways: the test suite must not touch that file either.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = (
    ROOT / ".claude" / "skills" / "watcher-runtime-state" / "scripts" / "write_runtime_state.py"
)


def _run(state_file: pathlib.Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(SCRIPT), "--state-file", str(state_file), *args],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )


def test_a_cycle_with_no_change_is_byte_identical(tmp_path: pathlib.Path) -> None:
    """Ruling 47(d)'s acceptance test, stated as the violation that must become
    impossible: a watcher cycle in which nothing changed must not move a single byte,
    freshness token included -- because a byte that does move while content is frozen is
    exactly register finding F31 (`docs/audit/register.md`)."""
    state_file = tmp_path / "runtime-state.json"

    first = _run(
        state_file,
        "cycle",
        "--phase",
        "2",
        "--phase-source",
        "docs/roadmap.md §7",
        "--work",
        "W11",
        "--work-source",
        "docs/roadmap.md §7",
    )
    assert first.returncode == 0
    first_bytes = state_file.read_bytes()

    # Real wall-clock time passes between cycles -- if the script naively stamped
    # "now" on every write regardless of content, this is exactly the gap that would
    # show up as a moved byte.
    time.sleep(1.1)

    second = _run(
        state_file,
        "cycle",
        "--phase",
        "2",
        "--phase-source",
        "docs/roadmap.md §7",
        "--work",
        "W11",
        "--work-source",
        "docs/roadmap.md §7",
    )
    assert second.returncode == 0
    second_bytes = state_file.read_bytes()

    assert second_bytes == first_bytes, (
        "a no-op cycle moved a byte -- a freshness token refreshed while its content "
        "stayed frozen, which is F31 regardless of what surrounds it"
    )


def test_a_cycle_that_omits_position_args_keeps_the_prior_position(
    tmp_path: pathlib.Path,
) -> None:
    """Omitting `--phase`/`--work` this cycle must not erase what a previous cycle
    recorded -- only an explicit new value overwrites a field."""
    state_file = tmp_path / "runtime-state.json"
    _run(state_file, "cycle", "--phase", "2", "--phase-source", "docs/roadmap.md §7")
    before = json.loads(state_file.read_text())

    time.sleep(1.1)
    result = _run(state_file, "cycle")
    assert result.returncode == 0
    after = json.loads(state_file.read_text())

    assert after == before


def test_retry_counters_is_never_present(tmp_path: pathlib.Path) -> None:
    """Ruling 47(c): `retry_counters` may not appear in B until NT-0014 script C2
    exists (adoption slice G, not yet built) -- a `0` from a counter nothing increments
    is indistinguishable from a true zero. Absent, never zero."""
    state_file = tmp_path / "runtime-state.json"
    _run(state_file, "cycle", "--phase", "2", "--phase-source", "docs/roadmap.md §7")
    doc = json.loads(state_file.read_text())
    assert "retry_counters" not in doc
    assert "retry_counters" not in doc["position"]


def test_flow_step_is_not_a_field_the_script_can_write(tmp_path: pathlib.Path) -> None:
    """Ruling 47(c): `flow_step` has no source artifact -- a running agent's belief
    about its own step is the `roster-state.md` claim verbatim -- so it is carried only
    if a source can be named, and dropped otherwise. This script names no source for it
    and therefore exposes no way to write it at all."""
    state_file = tmp_path / "runtime-state.json"
    _run(
        state_file,
        "cycle",
        "--phase",
        "2",
        "--phase-source",
        "docs/roadmap.md §7",
        "--work",
        "W11",
        "--work-source",
        "docs/roadmap.md §7",
    )
    doc = json.loads(state_file.read_text())
    assert "flow_step" not in doc["position"]


def test_no_file_level_updated_at(tmp_path: pathlib.Path) -> None:
    """Ruling 47(c): a single `updated_at` over the whole document is the F31 shape
    exactly -- one true field vouching for a document of frozen ones."""
    state_file = tmp_path / "runtime-state.json"
    _run(state_file, "cycle", "--phase", "2", "--phase-source", "docs/roadmap.md §7")
    doc = json.loads(state_file.read_text())
    assert "updated_at" not in doc
    assert "written_at" in doc["position"]  # per-block, not file-level


def test_position_fields_carry_their_source(tmp_path: pathlib.Path) -> None:
    """Ruling 47(c): position fields name the artifact they were read from."""
    state_file = tmp_path / "runtime-state.json"
    _run(
        state_file,
        "cycle",
        "--phase",
        "2",
        "--phase-source",
        "docs/roadmap.md §7",
        "--work",
        "W11",
        "--work-source",
        "docs/roadmap.md §7",
        "--slice",
        "W11-S3",
        "--slice-source",
        "docs/plans/2026-08-29-w11-map.md",
    )
    doc = json.loads(state_file.read_text())
    for field in ("phase", "work", "slice"):
        assert doc["position"][field]["read_from"], f"{field} has no read_from"


def test_an_in_flight_entry_expires_and_is_pruned_on_the_next_cycle(
    tmp_path: pathlib.Path,
) -> None:
    """`in_flight_expensive_verifications` is genuinely underivable from a durable
    artifact -- it is announced by a role about itself. Made falsifiable the other way:
    a 1-second TTL entry must be gone from the next cycle a second later."""
    state_file = tmp_path / "runtime-state.json"
    announce = _run(
        state_file,
        "announce",
        "--what",
        "full_test_suite",
        "--by",
        "auditor",
        "--tree",
        "1407e09",
        "--ttl-seconds",
        "1",
    )
    assert announce.returncode == 0
    doc = json.loads(state_file.read_text())
    assert len(doc["in_flight_expensive_verifications"]["entries"]) == 1

    time.sleep(1.5)
    result = _run(state_file, "cycle")
    assert result.returncode == 0
    doc = json.loads(state_file.read_text())
    assert doc["in_flight_expensive_verifications"]["entries"] == []


def test_a_still_live_in_flight_entry_survives_a_cycle(tmp_path: pathlib.Path) -> None:
    state_file = tmp_path / "runtime-state.json"
    _run(
        state_file,
        "announce",
        "--what",
        "full_test_suite",
        "--by",
        "auditor",
        "--tree",
        "1407e09",
        "--ttl-seconds",
        "3600",
    )
    result = _run(state_file, "cycle")
    assert result.returncode == 0
    doc = json.loads(state_file.read_text())
    assert len(doc["in_flight_expensive_verifications"]["entries"]) == 1


def test_only_the_block_that_actually_changed_is_rewritten(tmp_path: pathlib.Path) -> None:
    """Ruling 47(b)/(c): the watcher does not touch a block it did not write this
    cycle. Changing position must not move `in_flight_expensive_verifications`'s own
    `written_at`, and the reverse."""
    state_file = tmp_path / "runtime-state.json"
    _run(state_file, "cycle", "--phase", "2", "--phase-source", "docs/roadmap.md §7")
    first = json.loads(state_file.read_text())
    inflight_written_at = first["in_flight_expensive_verifications"]["written_at"]

    time.sleep(1.1)
    _run(state_file, "cycle", "--phase", "2b", "--phase-source", "docs/roadmap.md §7")
    second = json.loads(state_file.read_text())

    assert second["position"]["written_at"] != first["position"]["written_at"]
    assert second["in_flight_expensive_verifications"]["written_at"] == inflight_written_at


def test_a_corrupt_state_file_is_refused_rather_than_silently_overwritten(
    tmp_path: pathlib.Path,
) -> None:
    state_file = tmp_path / "runtime-state.json"
    state_file.write_text("{ not json")
    result = _run(state_file, "cycle", "--phase", "2", "--phase-source", "docs/roadmap.md §7")
    assert result.returncode != 0
    assert state_file.read_text() == "{ not json"
