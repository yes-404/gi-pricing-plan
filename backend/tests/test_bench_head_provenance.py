"""The head a bench script prints as provenance is its own checkout's, from any cwd (#1900).

`scripts/bench-compiled-for.py` and `scripts/bench-score-batch.py` print `tree: <head>` beside
their figures. Run from another repository, a `git rev-parse HEAD` with no repository named
would label the figure with that repository's head.
"""

from __future__ import annotations

import asyncio
import importlib.util
import os
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


@pytest.mark.parametrize(
    "var", ["GIT_DIR", "GIT_COMMON_DIR", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY"]
)
@pytest.mark.parametrize("name", ["bench-compiled-for", "bench-score-batch"])
def test_an_exported_git_variable_does_not_redirect_the_head(
    name: str, var: str, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An exported GIT_DIR and its kin (as inside a git hook) override `git -C`; the head
    printed as provenance must still be the script's own checkout's (#1900 audit Q6-A)."""
    other = tmp_path / "other"
    other.mkdir()
    _git(other, "init", "-q")
    (other / "f").write_text("x")
    _git(other, "add", "-A")
    _git(other, "commit", "-q", "-m", "other")

    module = _load(name)
    for k in [k for k in os.environ if k.startswith("GIT_")]:
        monkeypatch.delenv(k)
    own_head = _git(SCRIPTS.parent, "rev-parse", "HEAD")
    suffix = {"GIT_INDEX_FILE": "/index", "GIT_OBJECT_DIRECTORY": "/objects"}.get(var, "")
    monkeypatch.setenv(var, f"{other / '.git'}{suffix}")
    assert module._git_head() == own_head


class _StopAfterProvenanceError(Exception):
    pass


@pytest.mark.parametrize("name", ["bench-compiled-for", "bench-score-batch"])
def test_repo_and_tree_are_the_first_two_lines_printed(
    name: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """`repo:` then `tree:` come before anything else, ahead of the first database call
    (the first thing `main` does after them), so a figure is never read without its head."""
    module = _load(name)

    def boom(*_a: object, **_k: object) -> None:
        raise _StopAfterProvenanceError

    monkeypatch.setattr(module, "Database", boom)
    args = (1,) if name == "bench-compiled-for" else (1, 1, 1)
    with pytest.raises(_StopAfterProvenanceError):
        asyncio.run(module.main(*args))
    lines = capsys.readouterr().out.splitlines()
    assert lines == [f"repo: {module.REPO}", f"tree: {module._git_head()}"]
