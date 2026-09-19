"""`.claude/skills/watcher-runtime-state/scripts/write_runtime_state.py` -- the RFC-895
runtime state file (artifact B), rebuilt to RL-907's shape
(`docs/plans/2026-08-30-nt-0014-q1-q3-q4-rulings.md`).

RL-907 rejected the note's original design -- a state file the watcher writes and a
mismatch detector compares against artifact history -- because that design's actual
failure mode is agreement by vacancy: a dead or unwired writer leaves both sides reading
zero, so the mismatch never fires. The ruling requires the watcher to **re-derive**
rather than compare, and binds the result with four falsifiability conditions: no
file-level freshness token, `retry_counters` written only by its own dedicated writer
(never fabricated here as a placeholder zero -- RFC-895 script C2,
`scripts/hooks/retry_cap_hook.py`, landed in adoption slice G),
`in_flight_expensive_verifications` entries carry a TTL and expire, and position fields
name the artifact they were read from. RL-907(d) states the acceptance test as the
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
    """RL-907(d)'s acceptance test, stated as the violation that must become
    impossible: a watcher cycle in which nothing changed must not move a single byte,
    freshness token included -- because a byte that does move while content is frozen is
    exactly register finding F31 (`docs/findings/register.md`)."""
    state_file = tmp_path / "runtime-state.json"

    first = _run(
        state_file,
        "cycle",
        "--phase",
        "2",
        "--phase-source",
        "docs/roadmap.md §7",
        "--work",
        "WK-671",
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
        "WK-671",
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


def test_cycle_never_writes_retry_counters(tmp_path: pathlib.Path) -> None:
    """RL-907(c): a `0` from a counter nothing increments is indistinguishable from a
    true zero, so `retry_counters` is written only by its own dedicated writer
    (`scripts/hooks/retry_cap_hook.py`, RFC-895 script C2, adoption slice G) -- never by
    this script's `cycle`, which has no source artifact for it and must not fabricate
    one. (Renamed 2026-08-31 from `test_retry_counters_is_never_present`: C2 now exists
    and does write the block via a separate path, so the absolute claim in the old name
    was no longer true of the file as a whole -- only of what `cycle` itself writes.)"""
    state_file = tmp_path / "runtime-state.json"
    _run(state_file, "cycle", "--phase", "2", "--phase-source", "docs/roadmap.md §7")
    doc = json.loads(state_file.read_text())
    assert "retry_counters" not in doc
    assert "retry_counters" not in doc["position"]


def test_flow_step_is_not_a_field_the_script_can_write(tmp_path: pathlib.Path) -> None:
    """RL-907(c): `flow_step` has no source artifact -- a running agent's belief
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
        "WK-671",
        "--work-source",
        "docs/roadmap.md §7",
    )
    doc = json.loads(state_file.read_text())
    assert "flow_step" not in doc["position"]


def test_no_file_level_updated_at(tmp_path: pathlib.Path) -> None:
    """RL-907(c): a single `updated_at` over the whole document is the F31 shape
    exactly -- one true field vouching for a document of frozen ones."""
    state_file = tmp_path / "runtime-state.json"
    _run(state_file, "cycle", "--phase", "2", "--phase-source", "docs/roadmap.md §7")
    doc = json.loads(state_file.read_text())
    assert "updated_at" not in doc
    assert "written_at" in doc["position"]  # per-block, not file-level


def test_position_fields_carry_their_source(tmp_path: pathlib.Path) -> None:
    """RL-907(c): position fields name the artifact they were read from.

    **Its locators were updated 2026-09-19 (W37-7 Task 12) because the guard this slice
    added refused them, and was right to.** The `--slice-source` named a plan by a
    pre-migration dated filename that no longer exists — so the test written to prove
    *"position fields name the artifact they were read from"* was itself naming an
    artifact that was not there. (The retired spelling is not reproduced: check 36 forbids
    a pre-migration path form surviving outside `docs/REDIRECTS.csv`. It does not currently
    scan `tests/`, but being outside a checker's scope is an accident of scope, not a
    permission.)

    The assertion below is why it went unnoticed: it checks the field is **non-empty**,
    never that it **resolves**. A locator that dangles satisfies it exactly as well as one
    that works — which is the same shape as everything else this slice found, a check
    answering a narrower question than the one it appears to ask. The new tests below cover
    the half this one cannot, and this one is left asserting what it always asserted.
    """
    state_file = tmp_path / "runtime-state.json"
    _run(
        state_file,
        "cycle",
        "--phase",
        "2",
        "--phase-source",
        "docs/roadmap.md §6",
        "--work",
        "WK-697",
        "--work-source",
        "docs/roadmap.md §6",
        "--slice",
        "W37-7",
        "--slice-source",
        "docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md",
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
    """RL-907(b)/(c): the watcher does not touch a block it did not write this
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


# =========================================================================================
# R13-1 (plan review 13, `CR-1064:539`) -- a `read_from` locator whose file does not exist
# is refused, and nothing is written.
#
# The review found artifact B's live `position` block carrying two dangling locators. The
# values are not literals in this script: they arrive as `--*-source` arguments and are
# stored verbatim, so a repository commit cannot fix the live file -- only the instrument
# that writes it. Hence a fail-closed guard rather than a one-off correction.
#
# Validation stops at the **file path**. A `§n` suffix is prose and names no addressable
# thing, so there is nothing to resolve; claiming to check it would be a guard that cannot
# fail on its own stated subject.
# =========================================================================================


def test_a_dangling_source_path_is_refused_and_nothing_is_written(
    tmp_path: pathlib.Path,
) -> None:
    """Broken input: a `--*-source` whose file part does not resolve.

    Asserts **both** halves -- a non-zero exit *and* that the state file is unchanged --
    because a check that refuses and writes anyway is worse than one that does neither:
    it reports a failure the caller may ignore while the bad value lands regardless.
    """
    state_file = tmp_path / "runtime-state.json"

    seeded = _run(
        state_file,
        "cycle",
        "--phase",
        "2",
        "--phase-source",
        "docs/roadmap.md",
    )
    assert seeded.returncode == 0, seeded.stderr
    before = state_file.read_bytes()

    result = _run(
        state_file,
        "cycle",
        "--phase",
        "2",
        "--phase-source",
        "docs/this-file-does-not-exist.md §1",
    )

    assert result.returncode != 0, (
        "a locator whose file does not exist must be refused, not stored verbatim"
    )
    assert "does-not-exist" in result.stderr, result.stderr
    assert state_file.read_bytes() == before, (
        "the state file moved despite the refusal -- refusing and writing anyway is the "
        "worst of both"
    )


def test_a_resolvable_source_path_is_still_accepted(tmp_path: pathlib.Path) -> None:
    """Positive control. Without it, "refuses dangling locators" is indistinguishable
    from "refuses everything", and the guard above would pass while the instrument was
    entirely broken."""
    state_file = tmp_path / "runtime-state.json"

    result = _run(
        state_file,
        "cycle",
        "--phase",
        "2",
        "--phase-source",
        "docs/roadmap.md §6",
    )

    assert result.returncode == 0, result.stderr
    doc = json.loads(state_file.read_text(encoding="utf-8"))
    assert doc["position"]["phase"]["read_from"] == "docs/roadmap.md §6"


def test_the_suffix_is_not_what_is_validated(tmp_path: pathlib.Path) -> None:
    """The guard stops at the path, and says so by behaviour rather than by comment.

    `docs/roadmap.md` has no `## 99` heading, and this is still accepted: a `§n` suffix
    names no addressable thing, so there is nothing for the script to resolve. Pinning
    this stops a later reader "completing" the guard into a heading check that cannot be
    made to work.
    """
    state_file = tmp_path / "runtime-state.json"

    result = _run(
        state_file,
        "cycle",
        "--phase",
        "2",
        "--phase-source",
        "docs/roadmap.md §99",
    )

    assert result.returncode == 0, result.stderr


def test_every_source_argument_is_guarded_not_just_phase(tmp_path: pathlib.Path) -> None:
    """All three `--*-source` arguments, each checked independently.

    A guard wired into one argument's path and not the others passes any test that only
    exercises `--phase-source` -- which is the one the review happened to name.
    """
    for value_flag, source_flag, value in (
        ("--phase", "--phase-source", "2"),
        ("--work", "--work-source", "WK-697"),
        ("--slice", "--slice-source", "W37-7"),
    ):
        state_file = tmp_path / f"state{source_flag}.json"
        result = _run(
            state_file,
            "cycle",
            value_flag,
            value,
            source_flag,
            "docs/this-file-does-not-exist.md",
        )
        assert result.returncode != 0, f"{source_flag} is not guarded"
        assert not state_file.exists(), f"{source_flag} wrote a file despite refusing"
