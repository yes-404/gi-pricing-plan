"""`scripts/audit-docs.py` check 30: the vacated `.claude/notes/` tombstone is watched.

Ruling 61 (`docs/plans/2026-09-01-ruling-61-notes-tombstone-stubs-watched.md`) requires
this: NT-0016 Slice 4 kept 18 one-line redirect stubs at the vacated `.claude/notes/` path
(needed because a directory-level README alone does not make an individual old-path
citation inside a frozen plan resolve on disk — check 1's own requirement), but nothing in
`audit-docs.py` reads `.claude/notes/` any more once `NOTES` points at `docs/notes/`. Left
unwatched, a stray file or an edited stub body at the old path would be invisible to every
check in this script — exactly the unwatched-drift risk Ruling 57's own tombstone design
was chosen to avoid, recreated in a different shape. Check 30 closes that gap.

Same idiom as `tests/test_audit_docs_scan_roots.py`: a scratch mutation written into the
real tree and removed in `finally`, not a `tmp_path` copy — `audit-docs.py` derives `REPO`
from its own file location, so a copy outside the repo tree breaks every other path the
script resolves before the mutation under test is ever reached.

No `@pytest.mark.req` marker: this is correctness of the audit tool itself, not evidence
for a numbered platform requirement, the same reasoning the sibling scan-root and
finding-citation tests give their own unmarked tests.
"""

from __future__ import annotations

import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
OLD_NOTES = ROOT / ".claude" / "notes"
NOTES = ROOT / "docs" / "notes"


def _run_audit() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", "scripts/audit-docs.py"], capture_output=True, text=True, cwd=ROOT
    )


def test_the_unmodified_tombstone_passes() -> None:
    """Positive control: the tombstone as built (README + 18 stubs) is silent.

    The 18 *stubs* at the old path (`OLD_NOTES_STUB_NAMES` in `audit-docs.py`) are a
    frozen, closed registry that check 30 alone reads and never changes. The working-notes
    *count* asserted below is a different, unrelated number -- `check_notes()` reads
    `docs/notes/`, a disjoint root that keeps growing as notes are filed -- and this test
    used to restate it as the literal "18 working notes", true only because both numbers
    happened to coincide the day this test was written. That literal broke the very next
    day, when NT-0019 (PR #555) became the corpus's 19th note: a hardcoded count in a
    positive control breaks every time a note is legitimately added, which is the corpus
    behaving correctly, not a regression. Deriving `expected` from `docs/notes/` at run
    time -- the same directory, and the same "exclude README.md" rule, `check_notes()`
    itself uses -- means a future note never has to remember to bump a number here.
    """
    result = _run_audit()
    assert result.returncode == 0, result.stdout + result.stderr
    expected = len([p for p in NOTES.glob("*.md") if p.name != "README.md"])
    assert f"{expected} working notes" in result.stdout, result.stdout


def test_a_stray_file_at_the_old_path_fails() -> None:
    """Ruling 61 §4 case 1: an unregistered file at the vacated path must fail check 30,
    before its content is even read — the membership check catches it.
    """
    stray = OLD_NOTES / "0099-not-a-real-stub.md"
    stray.write_text("arbitrary content\n", encoding="utf-8")
    try:
        result = _run_audit()
        assert result.returncode != 0, result.stdout + result.stderr
        assert "0099-not-a-real-stub.md is not a registered stub" in result.stdout, (
            result.stdout
        )
    finally:
        stray.unlink()


def test_an_edited_stub_body_fails() -> None:
    """Ruling 61 §4 case 2: a registered stub whose content no longer matches its
    rendered template must fail check 30 — the case that matters most, a future
    contributor mistaking the old path for a place to write.
    """
    target = OLD_NOTES / "0007-context-bound-measures-cap-not-discipline.md"
    original = target.read_text(encoding="utf-8")
    target.write_text(original + "\nA sneaky appended sentence.\n", encoding="utf-8")
    try:
        result = _run_audit()
        assert result.returncode != 0, result.stdout + result.stderr
        assert (
            "0007-context-bound-measures-cap-not-discipline.md does not match its "
            "rendered template" in result.stdout
        ), result.stdout
    finally:
        target.write_text(original, encoding="utf-8")
