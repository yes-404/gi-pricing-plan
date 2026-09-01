"""NT-0016 Slice 4: after the notes move, the old notes root under `.claude` may be cited
only by its own tombstone, by files frozen under `docs/plans/README.md`'s write-once rule,
by check 30's own mechanism (Ruling 61 -- the check that *watches* the old path necessarily
names it), and by provenance-locked historical artifacts generated before the move landed.

This is the slice's own TDD leaf, per
`docs/plans/2026-08-31-nt-0016-investigation.md` §9 Step 1: the invariant the move must
establish, written and run to failure *before* the `git mv` of the notes directory to
`docs/notes` and the mechanism edits, rather than asserted after the fact. A count of living
citations differing from the plan's own re-derivation is expected -- the citation surface
moves day to day (see the plan's §1a) -- but the *classes* the citations fall into should
match what §1a and Ruling 58 of `docs/plans/2026-09-01-nt-0016-q4-q5-q6-q7-notes-rulings.md`
describe: frozen plans (untouched, C4), and everything else (edited by the move).

**Widened 2026-09-01 for Ruling 61** (`docs/plans/2026-09-01-ruling-61-notes-tombstone-
stubs-watched.md`): the ruled tombstone gained 18 per-file redirect stubs at the vacated
path plus a new check (30) that watches them, both landed after this test was first
written. The check's own implementation and its test necessarily and permanently name the
old path -- that is not a citation left behind by the move, it is the move's own watch
mechanism -- so `EXEMPT_FILES` below names them explicitly rather than widening the
`docs/plans/`-shaped carve-out to something looser. Two more exemptions came from a
rebase-time interaction, not from this slice's own work: `docs/audit/file-census-5ef559d.csv`
and `docs/audit/file-taxonomy-draft.md` (landed on `main` under PRs #537/#545 while this
branch was open) are provenance-locked snapshots of the tree as it stood at `4f95fb3`,
*before* this move -- editing either to say `docs/notes/` would misrepresent what was true
at the tree the filename itself pins, the same reason a frozen plan is not edited.

No `@pytest.mark.req` marker: this is a check on the repository's own citation surface, not
evidence for a numbered platform requirement -- the same reasoning
`tests/test_audit_docs_scan_roots.py` and `tests/test_audit_docs_finding_citations.py` give
their own unmarked tests.
"""

from __future__ import annotations

import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Check 30's own mechanism (Ruling 61): the code that watches the old path, its skill
# documentation, and its own test all name the old path deliberately and permanently.
_CHECK_30_MECHANISM = {
    "scripts/audit-docs.py",
    ".claude/skills/docs-audit/SKILL.md",
    "tests/test_audit_docs_notes_tombstone.py",
}

# Provenance-locked historical artifacts generated before this move landed (PRs #537/#545,
# tree 4f95fb3) -- frozen by the same reasoning as a docs/plans/ file, just outside that
# directory. Named explicitly rather than derived, so a future addition to this class does
# not silently widen the exemption without a reviewer seeing it.
_PRE_MOVE_SNAPSHOTS = {
    "docs/audit/file-census-5ef559d.csv",
    "docs/audit/file-taxonomy-draft.md",
}


def test_no_living_file_cites_the_old_notes_path() -> None:
    """After the move, the old notes root under `.claude` may be named only by the
    tombstone README left there, by files frozen under `docs/plans/`, by check 30's own
    watching mechanism, and by pre-move provenance-locked snapshots.

    A frozen plan is never edited to agree with a later move (`docs/plans/README.md`'s
    write-once rule, NT-0016 C4) -- the tombstone this slice creates at the vacated path
    is what keeps a path citation inside one of them resolving. Every other tracked file
    that still names the old path is a living citation this slice must repair.
    """
    # Built by concatenation, not written as one literal: this test file is itself part of
    # the tracked corpus it scans, and a literal occurrence of the old path in this source
    # line would make the test flag itself -- the self-referential trap a fixed offset or a
    # search term risks when the search runs over the file that states it.
    old_path = ".claude" + "/" + "notes"
    tracked = subprocess.run(
        ["git", "ls-files"], capture_output=True, text=True, cwd=ROOT, check=True
    ).stdout.split()
    exempt = _CHECK_30_MECHANISM | _PRE_MOVE_SNAPSHOTS
    offenders = [
        f
        for f in tracked
        if old_path in (ROOT / f).read_text(encoding="utf-8", errors="replace")
        and not f.startswith("docs/plans/")
        and f != old_path + "/README.md"
        and f not in exempt
    ]
    assert offenders == [], offenders
