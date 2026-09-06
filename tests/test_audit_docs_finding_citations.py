"""`scripts/audit-docs.py`'s check 25: an `F-id` cited outside the register must resolve.

Before this check existed, `audit-docs.py` validated `docs/findings/register.md` inward (every
§10 mirror row carries the register's status) but never outward: a citation from
`docs/research/`, `docs/plans/` or `docs/notes/` to a finding id was never checked against
anything. A draft citing a withdrawn `F42`, or a tombstone note promising `F45` hours before a
row existed for it, both reached `main` in the same week this check was written, caught only
because someone happened to remember the register's actual contents.

**The check's first version was itself wrong**, in the way that matters most for a governed
repository: it fired on *correct* behaviour. `F-W9-3-2` — a real finding, resolved the same day
it was raised, cited from the exact spec sentence it corrected (`03-rating-engine.md:671`) — has
no row in `docs/findings/register.md`, because the register's own header states its contract: one
row per *open* finding, removed when a close resolves it. A finding closed during its own
slice's audit is recorded in that slice's closure record
(`docs/audit/work/<slice>/README.md`'s Findings table) and never touches the live register at
all. Treating that as dangling would have shipped a check that fires on every properly-closed
finding in the repository — a worse defect than the gap it exists to catch, since a check that
cries wolf on real content teaches its readers to ignore it.

So this suite proves **both halves**, per the ruling that fixed the design: a genuinely dangling
id must still fire (`test_a_dangling_finding_id_is_refused`), and a real, closed,
correctly-recorded, correctly-cited finding must not
(`test_a_finding_resolved_only_by_a_closure_record_is_not_flagged`). A check shown only to fire
has not been shown to discriminate.

No `@pytest.mark.req` marker: this is correctness of the audit tool itself, not evidence for a
numbered platform requirement, the same reasoning `tests/test_scope_audit.py` gives for
`scope-audit.py`.
"""

from __future__ import annotations

import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "audit-docs.py"


def _run() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(SCRIPT)], capture_output=True, text=True, cwd=ROOT
    )


def test_a_dangling_finding_id_is_refused() -> None:
    """A citation to an id that resolves nowhere -- not the register, not any closure
    record, not defined locally -- must fail the audit and name both the file and the id.
    """
    scratch = ROOT / "docs" / "plans" / "zz-scratch-test-dangling-finding.md"
    scratch.write_text("# Scratch\n\nCites a bogus finding (F999999) here.\n", encoding="utf-8")
    try:
        result = _run()
        assert result.returncode != 0, result.stdout + result.stderr
        assert "F999999" in result.stdout, result.stdout
        assert "resolves nowhere" in result.stdout, result.stdout
        assert scratch.name in result.stdout, result.stdout
    finally:
        scratch.unlink()


def test_a_finding_resolved_only_by_a_closure_record_is_not_flagged() -> None:
    """`F-W9-3-2`: real, resolved 2026-08-27, recorded in `docs/closures/CR-00837-work-item-record-w9-3-bundle-compilation.md`'s
    Findings table, never filed to `register.md` (the register holds only open findings), and
    cited from `docs/rulings/INDEX.md#2026-08-29-w11-slice1-rulingsmd`. The check's first version, before
    this fix, flagged this exact citation as dangling -- the incident that forced the redesign.

    Pinned against the real tree rather than a synthetic fixture deliberately: this is the
    actual case that exposed the design gap, so it is the one case that must never regress.
    """
    closure_record = ROOT / "docs" / "audit" / "work" / "W9-3" / "README.md"
    assert "F-W9-3-2" in closure_record.read_text(encoding="utf-8"), (
        "the real-world case this test pins has moved or been renamed -- "
        "re-derive against the current closure record before trusting this test"
    )
    citing_file = ROOT / "docs" / "plans" / "2026-08-29-w11-slice1-rulings.md"
    assert "F-W9-3-2" in citing_file.read_text(encoding="utf-8"), (
        "the citation this test pins has moved -- re-derive before trusting this test"
    )

    result = _run()
    assert result.returncode == 0, result.stdout + result.stderr
    assert "All checks passed" in result.stdout, result.stdout
    assert "F-W9-3-2" not in result.stdout, (
        "F-W9-3-2 is real, closed and correctly cited -- it must never appear in "
        f"the audit's failure output:\n{result.stdout}"
    )
