"""The audit checks ADR 8449 keeps are still red on a planted fault.

Each case copies the audited part of the tree to a scratch directory, plants one fault, runs
that copy's `audit-docs.py` and requires the named check to print a failure, while the
unplanted copy passes. A check that has never printed a failure has not been tested
(CLAUDE.md §13).
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import _frozen  # type: ignore[import-not-found]  # noqa: E402

COPIED = (
    "scripts",
    "packages/model-schema/src",
    "backend/src/app",
    "CLAUDE.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    ".claude/skills",
    "docs/specs",
    "docs/workflows",
    "docs/adrs",
    "docs/process",
    "docs/contracts",
    "docs/_templates",
    "docs/README.md",
    "docs/skills-map.md",
    "docs/INDEX.md",
    "docs/REDIRECTS.csv",
    "docs/open-questions.md",
    ".claude/roles",
    ".claude/agents",
)


@pytest.fixture(scope="module")
def pristine(tmp_path_factory: pytest.TempPathFactory) -> Path:
    dest = tmp_path_factory.mktemp("kept-checks")
    for rel in COPIED:
        src = ROOT / rel
        if not src.exists():
            continue
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, target, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy2(src, target)
    # Frozen records are not audited, but REDIRECTS.csv rows name them: an empty stand-in
    # per tracked file keeps check 36's "target exists" clause honest without copying them.
    tracked = subprocess.run(
        ["git", "ls-files", "-z", "docs"], capture_output=True, text=True, cwd=ROOT, check=True
    ).stdout.split("\0")
    for rel in tracked:
        if rel and (dest / rel).exists() is False and _frozen.is_frozen(rel):
            (dest / rel).parent.mkdir(parents=True, exist_ok=True)
            (dest / rel).write_text("", encoding="utf-8")
    # Checks 30, 32, 35 and 36 fail only what the change's own diff introduces, so the copy is
    # a git repository whose first commit is the base the planted change is diffed against.
    _git(dest, "init", "-q")
    _git(dest, "add", "-A")
    _git(dest, "commit", "-q", "-m", "base")
    return dest


def _git(tree: Path, *args: str) -> str:
    env = {
        "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com",
        "PATH": os.environ["PATH"], "HOME": str(tree),
    }
    return subprocess.run(
        ["git", "-C", str(tree), *args], capture_output=True, text=True, check=True, env=env
    ).stdout.strip()


def _audit(tree: Path) -> subprocess.CompletedProcess[str]:
    """Commit whatever was planted, then audit with the pristine commit as the base."""
    base = _git(tree, "rev-list", "--max-parents=0", "HEAD")
    _git(tree, "add", "-A")
    _git(tree, "commit", "-q", "--allow-empty", "-m", "change")
    return subprocess.run(
        [sys.executable, str(tree / "scripts" / "audit-docs.py")],
        capture_output=True, text=True, cwd=tree,
        env={**os.environ, "AUDIT_DOCS_BASE": base},
    )


def _write(rel: str, text: str) -> Callable[[Path], None]:
    def plant(tree: Path) -> None:
        target = tree / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return plant


def _append(rel: str, text: str) -> Callable[[Path], None]:
    def plant(tree: Path) -> None:
        with (tree / rel).open("a", encoding="utf-8") as fh:
            fh.write(text)
    return plant


def _replace(rel: str, old: str, new: str, count: int = 1) -> Callable[[Path], None]:
    def plant(tree: Path) -> None:
        p = tree / rel
        text = p.read_text(encoding="utf-8")
        assert old in text, (rel, old)
        p.write_text(text.replace(old, new, count), encoding="utf-8")
    return plant


def _regex(rel: str, pattern: str, new: str) -> Callable[[Path], None]:
    def plant(tree: Path) -> None:
        p = tree / rel
        text = p.read_text(encoding="utf-8")
        out, n = re.subn(pattern, new, text, count=1, flags=re.M)
        assert n == 1, (rel, pattern)
        p.write_text(out, encoding="utf-8")
    return plant


SPEC = "docs/specs/07-platform.md"
ADR_OLD = (
    "docs/adrs/ADR-00703-pricing-core-is-dependency-free-and-owns-all-actuarial-maths.md"
)
ADR_NEW = (
    "docs/adrs/ADR-08449-project-management-moves-to-github-with-a-slim-claude-md-and-"
    "frozen-record-families.md"
)
CASES: dict[str, tuple[int, Callable[[Path], None]]] = {
    "1 broken relative link": (1, _append(SPEC, "\n[x](no-such-file.md)\n")),
    "2 citation of an undefined requirement": (2, _append(SPEC, "\nSee FR-9999999.\n")),
    "5 citation of an ADR with no file": (5, _append(SPEC, "\nSee ADR-9999.\n")),
    "6 spec missing a section": (6, _regex(SPEC, r"^## 10\..*$", "## ten")),
    "9 reference to a section that does not exist": (
        9, _append(SPEC, "\nSee 01 §99.9 for detail.\n")),
    "12 fractional money field": (12, _append(SPEC, "\n{\"premium_minor\": 12.5}\n")),
    "22 table row with a stray cell": (
        22, _append(SPEC, "\n| a | b |\n|---|---|\n| 1 | 2 | 3 |\n")),
    "7 duplicate key in a contract": (
        7, _replace("docs/contracts/schemas/model.schema.json", "{", '{"zz": 1, "zz": 2,')),
    "8 dangling $ref": (
        8, _regex("docs/contracts/schemas/model.schema.json",
                  r'"\$ref":\s*"#/\$defs/', '"$ref": "#/$defs/NoSuchDef')),
    "26 process core citing a section that does not exist": (
        26, _replace(
            "docs/process/delivery-process.core.json", '"source": "§3"', '"source": "§99"')),
    "27 process spec changed without the digest": (
        27, _append("docs/process/delivery-process.md", "\nOne more sentence.\n")),
    "34 corrected_by entry that does not point back": (
        34, _replace(ADR_OLD, "corrected_by: []", "corrected_by: [ADR-704]")),
    "30 header with an unknown field": (
        30, _replace(ADR_OLD,
                     "\nstatus:", "\nzz_unknown: 1\nstatus:")),
    "31 header id disagrees with the filename": (
        31, _replace(ADR_OLD,
                     "id: ADR-703", "id: ADR-704")),
    "32 citation of an id that is not in INDEX": (32, _append(SPEC, "\nSee PL-7777777.\n")),
    "33 status outside the vocabulary": (
        33, _replace(ADR_OLD,
                     "status: active", "status: bogus")),
    "35 owner that is not a role": (
        35, _replace(ADR_OLD,
                     "owner: ", "owner: nobody-here #")),
    "37 document missing a template section": (
        37, _regex(ADR_NEW, r"^## Decision\b.*$", "## Chosen")),
    "40 spec fence with no language": (40, _append(SPEC, "\n```\nplain\n```\n")),
    "30 new spec with no header": (30, _write("docs/specs/98-planted.md", "# a spec\n")),
    "36 new workflow citing a legacy path": (
        36, _write("docs/workflows/planted.md", "---\nx: 1\n---\nSee docs/audit/ for it.\n")),
}

LEGACY = "See docs/audit/ for it.\n"
#: The same faults outside the governed families, and old residue left alone: all green.
GREEN: dict[str, Callable[[Path], None]] = {
    "30 header-less skill": _write(".claude/skills/zz/SKILL.md", "# a skill\n"),
    "30 header-less generated contract": _write("docs/contracts/zz.json", "{}\n"),
    "35 skill front matter with a foreign owner": _write(
        ".claude/skills/zz/SKILL.md", "---\nname: zz\nowner: nobody\n---\nbody\n"),
    "36 skill citing a legacy path": _write(".claude/skills/zz/SKILL.md", LEGACY),
    "36 frozen record citing a legacy path": _write("docs/plans/zz.md", LEGACY),
    "30 edit to a spec that already had no header": _append(
        "docs/specs/00-overview.md", "\nOne harmless sentence.\n"),
}


def test_the_unplanted_copy_passes(pristine: Path) -> None:
    result = _audit(pristine)
    assert result.returncode == 0, result.stdout[-2000:] + result.stderr[-500:]


@pytest.mark.parametrize("case", sorted(CASES))
def test_a_planted_fault_reds_its_check(pristine: Path, tmp_path: Path, case: str) -> None:
    number, plant = CASES[case]
    work = tmp_path / "tree"
    shutil.copytree(pristine, work)
    plant(work)
    result = _audit(work)
    assert result.returncode != 0, case
    lines = [ln for ln in result.stdout.splitlines() if ln.startswith(f"  - check {number}:")]
    assert lines, (case, result.stdout[-1500:])


@pytest.mark.parametrize("case", sorted(GREEN))
def test_the_same_fault_outside_the_governed_families_is_green(
    pristine: Path, tmp_path: Path, case: str
) -> None:
    work = tmp_path / "tree"
    shutil.copytree(pristine, work)
    GREEN[case](work)
    result = _audit(work)
    assert result.returncode == 0, (case, result.stdout[-1500:])


def test_pre_existing_residue_is_counted_not_failed(pristine: Path) -> None:
    result = _audit(pristine)
    assert re.search(r"check 30: [1-9]\d* pre-existing violation", result.stdout), result.stdout
    assert re.search(r"check 36: [1-9]\d* pre-existing violation", result.stdout), result.stdout
