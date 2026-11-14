"""`scripts/freeze-check.py` — ADR-2136's freeze check, proven on planted changes in a
throwaway git repository: an edit, an add, a delete and a rename of a frozen path each
fail; an unfrozen path passes; a change already on the base is not read.

No `@pytest.mark.req` marker: governance-tool correctness, not evidence for a platform
requirement (same reasoning as `tests/test_doc_index.py`).
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "freeze-check.py"
sys.path.insert(0, str(SCRIPT.parent))  # `freeze-check.py` imports its sibling `_frozen`
_fz_spec = importlib.util.spec_from_file_location("_frozen", SCRIPT.parent / "_frozen.py")
assert _fz_spec is not None
assert _fz_spec.loader is not None
_frozen = importlib.util.module_from_spec(_fz_spec)
sys.modules["_frozen"] = _frozen
_fz_spec.loader.exec_module(_frozen)
FROZEN: tuple[str, ...] = _frozen.FROZEN

_spec = importlib.util.spec_from_file_location("freeze_check", SCRIPT)
assert _spec is not None
assert _spec.loader is not None
fc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fc)


def git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args],
        check=True, capture_output=True,
    )


def write(repo: Path, rel: str, text: str) -> None:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-q", "-b", "main")
    write(tmp_path, "docs/plans/PL-1.md", "plan\n")
    write(tmp_path, "docs/findings/register.md", "reg\n")
    write(tmp_path, "docs/roadmap.md", "road\n")
    write(tmp_path, "docs/specs/00.md", "spec\n")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-q", "-m", "base")
    git(tmp_path, "checkout", "-q", "-b", "work")
    return tmp_path


def run(repo: Path) -> int:
    code: int = fc.main(["--base", "main", "--repo", str(repo)])
    return code


def commit(repo: Path) -> None:
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "change")


def test_unfrozen_change_passes(repo: Path) -> None:
    write(repo, "docs/specs/00.md", "spec2\n")
    commit(repo)
    assert run(repo) == 0


@pytest.mark.parametrize(
    "rel", ["docs/plans/PL-1.md", "docs/findings/register.md", "docs/roadmap.md"]
)
def test_edit_of_a_frozen_file_fails(
    repo: Path, rel: str, capsys: pytest.CaptureFixture[str]
) -> None:
    write(repo, rel, "edited\n")
    commit(repo)
    assert run(repo) == 1
    out = capsys.readouterr().out
    assert out.startswith("freeze-check: FAIL head=")
    assert rel in out


@pytest.mark.parametrize("rel", [
    "docs/ledgers/LG-9.md", "docs/rulings/RL-9.md", "docs/closures/CR-9.md",
    "docs/findings/FD-9.md", "docs/rfcs/RFC-9.md", "docs/plans/PL-9.md",
])
def test_new_file_in_a_frozen_directory_fails(repo: Path, rel: str) -> None:
    write(repo, rel, "new\n")
    commit(repo)
    assert run(repo) == 1


def test_delete_and_rename_fail(repo: Path) -> None:
    git(repo, "mv", "docs/plans/PL-1.md", "docs/specs/PL-1.md")
    commit(repo)
    assert run(repo) == 1  # the removal from docs/plans/ is a change to it


def test_a_change_already_on_the_base_is_not_read(repo: Path) -> None:
    git(repo, "checkout", "-q", "main")
    write(repo, "docs/plans/PL-2.md", "landed on main after the branch point\n")
    commit(repo)
    git(repo, "checkout", "-q", "work")
    write(repo, "docs/specs/00.md", "spec2\n")
    commit(repo)
    git(repo, "merge", "-q", "--no-edit", "main")  # the branch re-merges main
    assert run(repo) == 0


def test_unknown_base_is_a_refusal_not_a_pass(repo: Path) -> None:
    assert fc.main(["--base", "no-such-ref", "--repo", str(repo)]) == 2


def _sample(entry: str) -> str:
    return entry + "x.md" if entry.endswith("/") else entry


@pytest.mark.parametrize("entry", FROZEN)
def test_every_entry_of_the_one_frozen_list_reds_on_an_edit(repo: Path, entry: str) -> None:
    """The list the script reads is the list this test reads: an entry added to FROZEN
    is proven red here without a second edit to the test."""
    rel = _sample(entry)
    base_has = (repo / rel).exists()
    write(repo, rel, "edited\n")
    commit(repo)
    assert run(repo) == 1, (rel, base_has)


@pytest.mark.parametrize("entry", FROZEN)
def test_every_entry_of_the_one_frozen_list_reds_on_a_delete(repo: Path, entry: str) -> None:
    rel = _sample(entry)
    git(repo, "checkout", "-q", "main")
    write(repo, rel, "present\n")
    commit(repo)
    git(repo, "checkout", "-q", "-B", "work")
    (repo / rel).unlink()
    commit(repo)
    assert run(repo) == 1
