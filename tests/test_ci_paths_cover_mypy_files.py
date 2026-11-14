"""Every `[tool.mypy] files` entry is matched by a `python.yml` path filter, in both trigger
lists (F26).

mypy and `ruff check .` run in `python.yml`, which runs only when a changed path matches its
`on.push.paths` or `on.pull_request.paths`. A directory mypy covers but the filters do not name
is checked by nothing when it changes alone: `.claude/skills/balance-watch/scripts` and
`.claude/skills/watcher-runtime-state/scripts` were exactly that. This pairs the two lists.

A `files` entry is a file or a directory; it is covered when some filter matches the entry
itself or a file under it. A filter is read the way GitHub reads it: `*` matches within one path
segment, `**` across segments.

No `@pytest.mark.req` marker: CI path coverage is the repository's own rule, not a numbered
platform requirement.
"""

from __future__ import annotations

import pathlib
import re
import tomllib

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "python.yml"


def _mypy_files() -> list[str]:
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return list(config["tool"]["mypy"]["files"])


def _trigger_paths(workflow: str) -> dict[str, list[str]]:
    """The `paths:` globs of each trigger under `on:`, read from the workflow text (no YAML
    dependency): a trigger is a two-space-indented key, a glob a `- '...'` item below `paths:`."""
    paths: dict[str, list[str]] = {}
    trigger: str | None = None
    in_paths = False
    for line in workflow.splitlines():
        if re.match(r"^\S", line):
            trigger, in_paths = None, False
        if m := re.match(r"^  (\w+):\s*$", line):
            trigger, in_paths = m.group(1), False
        elif re.match(r"^    paths:\s*$", line) and trigger:
            in_paths = True
            paths.setdefault(trigger, [])
        elif re.match(r"^    \S", line):
            in_paths = False
        elif in_paths and trigger and (item := re.match(r"^\s+- ['\"]?([^'\"#\s]+)['\"]?", line)):
            paths[trigger].append(item.group(1))
    return paths


def _matches(glob: str, path: str) -> bool:
    regex = ""
    i = 0
    while i < len(glob):
        if glob.startswith("**", i):
            regex += ".*"
            i += 2
        elif glob[i] == "*":
            regex += "[^/]*"
            i += 1
        else:
            regex += re.escape(glob[i])
            i += 1
    return re.fullmatch(regex, path) is not None


def uncovered(files: list[str], globs: list[str]) -> list[str]:
    """The `files` entries no glob matches, as the entry or as a file beneath it."""
    return [
        entry
        for entry in files
        if not any(_matches(g, entry) or _matches(g, f"{entry}/probe.py") for g in globs)
    ]


@pytest.mark.parametrize("trigger", ["push", "pull_request"])
def test_every_mypy_covered_path_triggers_python_yml(trigger: str) -> None:
    globs = _trigger_paths(WORKFLOW.read_text(encoding="utf-8"))[trigger]
    assert globs, f"no paths read for the {trigger} trigger"
    assert uncovered(_mypy_files(), globs) == []


def test_the_pairing_fails_on_a_mypy_directory_no_filter_names() -> None:
    """Red on deliberately broken input: the filters of the base tree, which named one skill
    directory only, leave the other two uncovered; a glob for them clears it."""
    base = ["packages/**", "backend/**", "scripts/**", "examples/**", "tests/**",
            ".claude/skills/reporter-cycle/**"]  # fmt: skip
    assert uncovered(_mypy_files(), base) == [
        ".claude/skills/balance-watch/scripts",
        ".claude/skills/watcher-runtime-state/scripts",
    ]
    assert uncovered(_mypy_files(), [*base, ".claude/skills/*/**"]) == []


def test_the_glob_reader_takes_each_trigger_and_its_own_list() -> None:
    text = (
        "on:\n  push:\n    branches: [main]\n    paths:\n      - 'a/**'  # why\n"
        "  pull_request:\n    paths:\n      - \"b/**\"\n      - 'c.py'\njobs:\n  x:\n"
        "    paths:\n      - 'ignored/**'\n"
    )
    assert _trigger_paths(text) == {"push": ["a/**"], "pull_request": ["b/**", "c.py"]}
