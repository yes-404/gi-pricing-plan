"""`scripts/hooks/retry_cap_hook.py` -- NT-0014 script C2, the retry-cap hook.

`docs/plans/2026-08-30-w11-reopen-hooks-and-bundle-resolution-rulings.md`, Ruling 40 §5,
states the standard this file exists to meet: a hook proven once by hand is "a check that
has never printed a failure", and the harness must be a repository test that runs in the
gate, drives the hook's entry point with a synthetic runtime state at the cap boundary,
and asserts **both halves** of the on-breach rule -- the retry is refused and the
notification is produced -- carrying a negative control one below the cap that must pass
through, "so the harness cannot go green by refusing everything."

Every case runs the script as a real subprocess against a `tmp_path`-scoped state file
and a `tmp_path`-scoped core-extract fixture (never the real `docs/process/
delivery-process.core.json`, so this suite's cap values are pinned and do not drift if
that file's real caps ever change) -- the same isolation discipline `tests/
test_watcher_runtime_state.py` applies to the real
`~/gi-pricing-plan.local/handover/runtime-state.json`.

No `@pytest.mark.req` marker: correctness of a process-mechanism script, not evidence for
a numbered platform requirement (same posture as `tests/test_watcher_runtime_state.py`
and `tests/test_scope_audit.py`).
"""

from __future__ import annotations

import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "hooks" / "retry_cap_hook.py"

CAP = 2  # arbitrary fixture value -- deliberately different from reading the real extract


def _core_file(tmp_path: pathlib.Path, cap: int = CAP) -> pathlib.Path:
    core = tmp_path / "core.json"
    core.write_text(
        json.dumps({"guards": {"retry_caps": {"values": {"slice": cap, "work": 1}}}}),
        encoding="utf-8",
    )
    return core


def _run(
    state_file: pathlib.Path, core_file: pathlib.Path, *args: str, stdin: str | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "python3",
            str(SCRIPT),
            "--state-file",
            str(state_file),
            "--core-file",
            str(core_file),
            *args,
        ],
        input=stdin,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )


def _record(
    state_file: pathlib.Path,
    core_file: pathlib.Path,
    *,
    id_: str = "S1",
    kind: str = "fix",
    evidence: str = "PR #1",
) -> subprocess.CompletedProcess[str]:
    return _run(
        state_file,
        core_file,
        "record",
        "--layer",
        "slice",
        "--id",
        id_,
        "--kind",
        kind,
        "--evidence",
        evidence,
    )


# ---------------------------------------------------------------------------
# Ruling 40 §5's own acceptance test: cap+1 refused, cap-1 (negative control) allowed.
# ---------------------------------------------------------------------------


def test_a_cap_breaching_retry_is_refused_and_a_notification_is_produced(
    tmp_path: pathlib.Path,
) -> None:
    state_file = tmp_path / "runtime-state.json"
    core_file = _core_file(tmp_path, cap=CAP)

    # Bring the counter to exactly the cap (CAP successful records)...
    for i in range(CAP):
        result = _record(state_file, core_file, evidence=f"PR #{i}")
        assert result.returncode == 0, result.stderr

    # ...then the (CAP+1)-th attempt is the breach.
    breach = _record(state_file, core_file, evidence="PR #breach")
    assert breach.returncode == 1, "a cap-breaching retry must be refused, not recorded"
    assert "RETRY CAP BREACHED" in breach.stderr

    doc = json.loads(state_file.read_text())
    # Both halves of the on-breach rule: refused, AND a notification is produced.
    assert doc["retry_counters"]["entries"]["slice:S1:fix"]["count"] == CAP, (
        "a refused retry must not itself be counted"
    )
    checkpoint = doc["pending_human_checkpoint"]
    assert checkpoint is not None, "a breach must write a durable human notification"
    assert checkpoint["layer"] == "slice"
    assert checkpoint["id"] == "S1"
    assert checkpoint["kind"] == "fix"
    assert checkpoint["cap"] == CAP
    assert checkpoint["attempted_count"] == CAP + 1


def test_negative_control_one_below_cap_passes_through(tmp_path: pathlib.Path) -> None:
    """The control this class of harness is most exposed to: it must not go green by
    refusing everything. One below the cap must be recorded, not blocked."""
    state_file = tmp_path / "runtime-state.json"
    core_file = _core_file(tmp_path, cap=CAP)

    for i in range(CAP - 1):
        result = _record(state_file, core_file, evidence=f"PR #{i}")
        assert result.returncode == 0, result.stderr

    doc = json.loads(state_file.read_text())
    assert doc["retry_counters"]["entries"]["slice:S1:fix"]["count"] == CAP - 1
    assert doc.get("pending_human_checkpoint") is None, (
        "a retry within the cap must not produce a breach notification"
    )


# ---------------------------------------------------------------------------
# The `hook` PreToolUse entry point -- same decision, reached via the stdin/stdout
# contract Claude Code actually uses, not the `record` CLI directly.
# ---------------------------------------------------------------------------


def test_hook_denies_a_cap_breaching_record_invocation_before_it_runs(
    tmp_path: pathlib.Path,
) -> None:
    state_file = tmp_path / "runtime-state.json"
    core_file = _core_file(tmp_path, cap=CAP)
    for i in range(CAP):
        assert _record(state_file, core_file, evidence=f"PR #{i}").returncode == 0

    command = (
        f"python3 {SCRIPT} record --layer slice --id S1 --kind fix --evidence 'PR #next'"
    )
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    result = _run(state_file, core_file, "hook", stdin=payload)
    assert result.returncode == 0  # the hook process itself always exits 0; the JSON decides
    out = json.loads(result.stdout)
    assert out["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "systemMessage" in out
    assert "RETRY CAP BREACHED" in out["systemMessage"]

    # The retry never ran (the hook denied it before `record` executed), so the counter
    # itself must be untouched by this call -- but the notification must still land,
    # because in this path `record` never runs to write it.
    doc = json.loads(state_file.read_text())
    assert doc["retry_counters"]["entries"]["slice:S1:fix"]["count"] == CAP
    assert doc["pending_human_checkpoint"] is not None


def test_hook_allows_a_within_cap_record_invocation(tmp_path: pathlib.Path) -> None:
    state_file = tmp_path / "runtime-state.json"
    core_file = _core_file(tmp_path, cap=CAP)

    command = f"python3 {SCRIPT} record --layer slice --id S2 --kind fix --evidence x"
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    result = _run(state_file, core_file, "hook", stdin=payload)
    out = json.loads(result.stdout)
    assert out["hookSpecificOutput"]["permissionDecision"] == "allow"
    # An allow decision alone must not itself write a breach notification.
    doc = json.loads(state_file.read_text()) if state_file.exists() else {}
    assert doc.get("pending_human_checkpoint") is None


def test_hook_allows_an_unrelated_bash_command_unexamined(tmp_path: pathlib.Path) -> None:
    """A mis-parse or a non-matching command must never falsely block -- only a
    confirmed breach may."""
    state_file = tmp_path / "runtime-state.json"
    core_file = _core_file(tmp_path, cap=CAP)
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": "ls -la"}})
    result = _run(state_file, core_file, "hook", stdin=payload)
    out = json.loads(result.stdout)
    assert out["hookSpecificOutput"]["permissionDecision"] == "allow"


def test_hook_allows_on_empty_or_malformed_stdin(tmp_path: pathlib.Path) -> None:
    state_file = tmp_path / "runtime-state.json"
    core_file = _core_file(tmp_path, cap=CAP)
    result = _run(state_file, core_file, "hook", stdin="not json at all")
    assert result.returncode == 0
    out = json.loads(result.stdout)
    assert out["hookSpecificOutput"]["permissionDecision"] == "allow"


# ---------------------------------------------------------------------------
# Bypass honesty: record() enforces the cap on its own, independent of the hook wiring
# -- this is the property the module docstring claims and the report must not overstate.
# ---------------------------------------------------------------------------


def test_record_enforces_the_cap_even_when_never_reached_via_the_hook(
    tmp_path: pathlib.Path,
) -> None:
    """`record` run directly (as if hooks were disabled, or invoked from a plain
    terminal) must still refuse a breach -- the enforcement does not depend on the
    PreToolUse wiring being active."""
    state_file = tmp_path / "runtime-state.json"
    core_file = _core_file(tmp_path, cap=CAP)
    for i in range(CAP):
        assert _record(state_file, core_file, evidence=f"PR #{i}").returncode == 0
    breached = _record(state_file, core_file, evidence="PR #direct")
    assert breached.returncode == 1


def test_a_direct_hand_edit_of_the_state_file_is_not_stopped_by_anything_here(
    tmp_path: pathlib.Path,
) -> None:
    """States plainly, as a passing test rather than only as prose, the limit the module
    docstring claims: nothing in this script stops an actor from hand-editing
    retry_counters directly, bypassing both `record` and `hook` entirely. This is not a
    defect to fix in this slice -- Ruling 40 dissolved C3 for exactly this class of gap
    in a git hook, and C2 inherits the same limit for the same reason (no in-repo
    mechanism can intercept a plain file write)."""
    state_file = tmp_path / "runtime-state.json"
    state_file.write_text(
        json.dumps(
            {
                "retry_counters": {
                    "entries": {"slice:S1:fix": {"count": 999, "evidence": []}}
                }
            }
        ),
        encoding="utf-8",
    )
    assert json.loads(state_file.read_text())["retry_counters"]["entries"]["slice:S1:fix"][
        "count"
    ] == 999


# ---------------------------------------------------------------------------
# `clear-checkpoint`
# ---------------------------------------------------------------------------


def test_clear_checkpoint_resets_it_to_null(tmp_path: pathlib.Path) -> None:
    state_file = tmp_path / "runtime-state.json"
    core_file = _core_file(tmp_path, cap=CAP)
    for i in range(CAP):
        assert _record(state_file, core_file, evidence=f"PR #{i}").returncode == 0
    assert _record(state_file, core_file, evidence="PR #breach").returncode == 1
    assert json.loads(state_file.read_text())["pending_human_checkpoint"] is not None

    result = _run(state_file, core_file, "clear-checkpoint")
    assert result.returncode == 0
    assert json.loads(state_file.read_text())["pending_human_checkpoint"] is None


# ---------------------------------------------------------------------------
# Unknown layer / corrupt state
# ---------------------------------------------------------------------------


def test_unknown_layer_is_refused_rather_than_silently_uncapped(tmp_path: pathlib.Path) -> None:
    state_file = tmp_path / "runtime-state.json"
    core_file = _core_file(tmp_path, cap=CAP)
    result = _run(
        state_file,
        core_file,
        "record",
        "--layer",
        "galaxy",
        "--id",
        "X",
        "--kind",
        "fix",
        "--evidence",
        "x",
    )
    assert result.returncode != 0


def test_a_corrupt_state_file_is_refused_rather_than_silently_overwritten(
    tmp_path: pathlib.Path,
) -> None:
    state_file = tmp_path / "runtime-state.json"
    core_file = _core_file(tmp_path, cap=CAP)
    state_file.write_text("{ not json")
    result = _record(state_file, core_file)
    assert result.returncode != 0
    assert state_file.read_text() == "{ not json"
