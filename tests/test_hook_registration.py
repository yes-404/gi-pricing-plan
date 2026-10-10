"""The PreToolUse hook REGISTERED in `.claude/settings.json` runs from any working directory.

`tests/test_retry_cap_hook.py` runs the script by its absolute path, so it never sees the command
Claude Code actually executes. This file reads that command out of the tracked settings file and
runs it the way the harness does (`sh -c`, the tool call on stdin) from a subdirectory. A
cwd-relative path made `python3` exit 2 -- a blocking exit -- on every Bash call after a `cd`
(PL 9617, FD 9959). The `if` filter is best-effort by documented design, so the command itself
must work from any cwd.

No `@pytest.mark.req` marker: a process-mechanism test, the same posture as
`tests/test_retry_cap_hook.py`.
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
from typing import Any

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SETTINGS = ROOT / ".claude" / "settings.json"
SCRIPT_RELPATH = "scripts/hooks/retry_cap_hook.py"
_REPO_SCRIPT_PATH = re.compile(r"scripts/hooks/[\w./-]+")

# A layer whose cap in docs/process/delivery-process.core.json is 1: seeded at 1 the next record
# breaches, seeded at 0 it is within the cap.
_CAPPED_LAYER = "project"


def _registered_commands(settings: pathlib.Path = SETTINGS) -> list[str]:
    doc = json.loads(settings.read_text(encoding="utf-8"))
    return [
        hook["command"]
        for group in doc["hooks"]["PreToolUse"]
        for hook in group["hooks"]
        if hook.get("type") == "command"
    ]


def _unanchored_repo_paths(command: str) -> list[str]:
    """Repository script paths the command names that are not preceded by `/` (a cwd-relative
    path, or one glued to something that is not a directory)."""
    return [
        m.group(0)
        for m in _REPO_SCRIPT_PATH.finditer(command)
        if m.start() == 0 or command[m.start() - 1] != "/"
    ]


def _run_registered(
    command: str,
    *,
    cwd: pathlib.Path,
    tool_command: str,
    state_file: pathlib.Path,
    project_dir: str | None,
) -> subprocess.CompletedProcess[str]:
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
    env["RUNTIME_STATE_FILE"] = str(state_file)
    if project_dir is not None:
        env["CLAUDE_PROJECT_DIR"] = project_dir
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": tool_command}})
    return subprocess.run(
        ["sh", "-c", command],
        input=payload,
        capture_output=True,
        text=True,
        cwd=cwd,
        env=env,
        check=False,
    )


def _decision(result: subprocess.CompletedProcess[str]) -> str:
    assert result.returncode == 0, result.stderr
    out: dict[str, Any] = json.loads(result.stdout)
    decision: str = out["hookSpecificOutput"]["permissionDecision"]
    return decision


def _seed(state_file: pathlib.Path, count: int) -> None:
    key = f"{_CAPPED_LAYER}:P1:fix"
    state_file.write_text(
        json.dumps({"retry_counters": {"entries": {key: {"count": count}}}}), encoding="utf-8"
    )


def _record_call(evidence: str = "x") -> str:
    return (
        f"python3 {ROOT / SCRIPT_RELPATH} record --layer {_CAPPED_LAYER} --id P1 "
        f"--kind fix --evidence {evidence}"
    )


# CLAUDE_PROJECT_DIR set (the documented case) and unset (a teammate's hook process is not
# documented to get it; DP-1's `git rev-parse` fallback must carry it).
_PROJECT_DIRS = [pytest.param(str(ROOT), id="project-dir-set"), pytest.param(None, id="unset")]
_CWDS = [pytest.param("docs", id="from-docs"), pytest.param(".", id="from-root")]


@pytest.mark.parametrize("project_dir", _PROJECT_DIRS)
@pytest.mark.parametrize("cwd", _CWDS)
def test_registered_command_allows_an_unrelated_call_from_any_cwd(
    tmp_path: pathlib.Path, cwd: str, project_dir: str | None
) -> None:
    for command in _registered_commands():
        result = _run_registered(
            command,
            cwd=ROOT / cwd,
            tool_command='echo "$(pwd)" | cat',
            state_file=tmp_path / "state.json",
            project_dir=project_dir,
        )
        assert _decision(result) == "allow"


@pytest.mark.parametrize("project_dir", _PROJECT_DIRS)
def test_registered_command_still_denies_a_cap_breaching_record_from_docs(
    tmp_path: pathlib.Path, project_dir: str | None
) -> None:
    """Proof (iii): the hook still refuses what it refused before, via the registered command."""
    state_file = tmp_path / "state.json"
    _seed(state_file, count=1)
    for command in _registered_commands():
        result = _run_registered(
            command,
            cwd=ROOT / "docs",
            tool_command=_record_call(),
            state_file=state_file,
            project_dir=project_dir,
        )
        assert _decision(result) == "deny"


def test_registered_command_allows_a_within_cap_record_from_docs(tmp_path: pathlib.Path) -> None:
    """The negative control: the refusal above is not a refusal of everything."""
    state_file = tmp_path / "state.json"
    _seed(state_file, count=0)
    for command in _registered_commands():
        result = _run_registered(
            command,
            cwd=ROOT / "docs",
            tool_command=_record_call(),
            state_file=state_file,
            project_dir=str(ROOT),
        )
        assert _decision(result) == "allow"


def test_no_registered_command_names_a_repository_path_relatively() -> None:
    commands = _registered_commands()
    assert commands, "no PreToolUse command hook is registered"
    for command in commands:
        assert _unanchored_repo_paths(command) == [], command
        for rel in _REPO_SCRIPT_PATH.findall(command):
            assert (ROOT / rel).is_file(), f"{rel} is registered but missing under the repo root"


def test_the_anchoring_check_fails_on_the_old_relative_form(tmp_path: pathlib.Path) -> None:
    """Broken-input proof: the walk above is not vacuous."""
    old = "python3 scripts/hooks/retry_cap_hook.py hook"
    scratch = tmp_path / "settings.json"
    scratch.write_text(
        json.dumps({"hooks": {"PreToolUse": [{"hooks": [{"type": "command", "command": old}]}]}}),
        encoding="utf-8",
    )
    (command,) = _registered_commands(scratch)
    assert _unanchored_repo_paths(command) == [SCRIPT_RELPATH]
