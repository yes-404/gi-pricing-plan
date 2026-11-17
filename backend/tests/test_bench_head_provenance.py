"""The head a bench script prints as provenance is its own checkout's, from any cwd (#1900).

`scripts/bench-compiled-for.py` and `scripts/bench-score-batch.py` print `tree: <head>` beside
their figures. Run from another repository, a `git rev-parse HEAD` with no repository named
would label the figure with that repository's head.
"""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2] / "scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), SCRIPTS / f"{name}.py")
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git(repo: pathlib.Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


@pytest.mark.parametrize("name", ["bench-compiled-for", "bench-score-batch"])
def test_git_head_is_the_scripts_own_checkout_from_another_repository(
    name: str, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    other = tmp_path / "other"
    other.mkdir()
    _git(other, "init", "-q")
    (other / "f").write_text("x")
    _git(other, "add", "-A")
    _git(other, "commit", "-q", "-m", "other")
    other_head = _git(other, "rev-parse", "HEAD")

    module = _load(name)
    own_head = _git(SCRIPTS.parent, "rev-parse", "HEAD")
    assert own_head != other_head
    monkeypatch.chdir(other)
    assert module._git_head() == own_head
