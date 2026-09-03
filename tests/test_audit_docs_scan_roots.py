"""`scripts/audit-docs.py`: a configured scan root that has vanished must fail, not skip.

Before this fix, `check_notes` (checks 16-20) and `check_finding_citations`'s `scan_dirs`
(check 25) both guard on `NOTES` existing and silently drop out when it does not:
`check_notes` appends an informational "checks 16-20 skipped" note and returns, and
`scan_dirs`'s `if d.is_dir()` filter drops the directory from the scan with no message at
all. Proven at `b551060` (`docs/plans/2026-08-31-nt-0016-investigation.md` §1b), when `NOTES`
still pointed under `.claude`: loading the script as a module, repointing `NOTES` at a
non-existent path and calling `main()` printed the skip line and "All checks passed." and
exited 0. A `git mv` of that directory for any reason -- not only NT-0016's planned move --
would leave the gate green while five checks stopped running.

Re-run against the moved root after NT-0016 Slice 4 (`NOTES` now `docs/notes/`) to confirm
the fix still watches: a green audit after a directory move proves nothing on its own, per
the plan's §9 Step 8 -- this is that proof, kept live rather than a one-time note.

No `@pytest.mark.req` marker: this is correctness of the audit tool itself, not evidence for
a numbered platform requirement, the same reasoning the sibling scan-root and finding-
citation tests give.
"""

from __future__ import annotations

import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "audit-docs.py"


def test_a_missing_notes_root_fails_the_audit() -> None:
    """A configured scan root that has vanished must be an error, never a skip.

    Before this test, repointing NOTES at a non-existent path left the audit printing
    "no <notes root> directory -- checks 16-20 skipped" and exiting 0, so a `git mv`
    of that directory would have silently un-watched five checks.

    The patched copy is written inside `scripts/`, not a bare `tmp_path`: `audit-docs.py`
    derives `REPO = pathlib.Path(__file__).resolve().parent.parent` (line 64), so a copy
    placed anywhere outside the repo tree breaks every other path the script resolves
    (`docs/open-questions.md` first) before the NOTES mutation is ever exercised -- a
    harness defect, not a discriminator on the behaviour under test. Same idiom as
    `test_audit_docs_finding_citations.py`: a scratch file written into the real tree and
    removed in `finally`.
    """
    source = SCRIPT.read_text(encoding="utf-8")
    # `NOTES` became a two-candidate lookup at W37-6 (`docs/notes/` pre-migration,
    # `docs/rfcs/` after it), so the constant is no longer a single literal path. The canary
    # moves with it: what this test needs is the *definition line*, whatever it now names,
    # and it still refuses to run if that line has changed shape again.
    definition = "NOTES = _first_dir("
    assert definition in source, (
        "the NOTES constant has moved -- re-derive this test before trusting it"
    )
    line = next(ln for ln in source.splitlines() if ln.startswith(definition))
    patched = SCRIPT.parent / "_scratch_audit_docs_scan_roots.py"
    patched.write_text(
        source.replace(line, 'NOTES = ROOT / "notes-that-do-not-exist"'),
        encoding="utf-8",
    )
    try:
        result = subprocess.run(
            ["python3", str(patched)], capture_output=True, text=True, cwd=ROOT
        )
        assert result.returncode != 0, result.stdout + result.stderr
        assert "notes-that-do-not-exist" in result.stdout, result.stdout
    finally:
        patched.unlink()
