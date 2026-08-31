"""`scripts/audit-docs.py`'s check 28: a filed plan states an explicit acceptance standard.

NT-0014 §2's C1 mechanises `delivery-process.md` §5 step 4 / §6 step 1 — the lead's
replan-vs-proceed check that "an acceptance standard was actually defined, not just
implied." The note's own draft mechanism ("warn until the format lands, red thereafter")
was **rejected** by Ruling 46
(`docs/plans/2026-08-30-nt-0014-q1-q3-q4-rulings.md`): a time-of-run switch makes the same
file pass on Tuesday and fail on Wednesday, and a fresh clone cannot reproduce a verdict.

Ruling 46 ruled a durable discriminator instead: **the plan's own filename date against a
constant cutoff** (`PLAN_ACCEPTANCE_STANDARD_CUTOFF` in the script) — no warn phase, because
C1 and the `writing-plans` acceptance-standard field land in the same commit. §3 of the
ruling requires three cases, "not one", because a check proven only to fire has not been
shown to discriminate:

- a synthetic plan **dated after the cutoff with no acceptance-standard field REDS**
  (`test_a_plan_after_the_cutoff_missing_the_field_is_refused`);
- a plan **dated before the cutoff PASSES** even with no field — the "never retro-red-gate"
  half (`test_a_legacy_plan_before_the_cutoff_is_never_flagged`);
- a **conforming plan dated after the cutoff PASSES** — the positive control, without which
  the check could go green by exempting everything
  (`test_a_conforming_plan_after_the_cutoff_is_not_flagged`).

Also checked: a bare "Acceptance Standard" heading with nothing under it before the next
heading is "implied", not "actually defined", and must still red
(`test_a_bare_heading_with_no_content_is_refused`).

No `@pytest.mark.req` marker: this is correctness of the audit tool itself, not evidence for
a numbered platform requirement, the same reasoning `tests/test_scope_audit.py` gives for
`scope-audit.py` and `tests/test_audit_docs_finding_citations.py` gives for check 25.
"""

from __future__ import annotations

import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "audit-docs.py"
PLANS = ROOT / "docs" / "plans"


def _run() -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python3", str(SCRIPT)], capture_output=True, text=True, cwd=ROOT)


def test_a_plan_after_the_cutoff_missing_the_field_is_refused() -> None:
    """A plan filed on/after the cutoff with no "Acceptance Standard" heading must fail the
    audit and name the file. The title deliberately avoids the phrase "acceptance standard"
    itself, so the check's own red-path proof is not accidentally satisfied by the fixture's
    title matching the heading it is supposed to be missing.
    """
    scratch = PLANS / "2026-08-31-zz-scratch-check28-missing-field.md"
    scratch.write_text(
        "# Scratch plan for check 28's red path\n\n"
        "**Goal:** exercise the missing-field case.\n\n"
        "## Global Constraints\n\nNone.\n",
        encoding="utf-8",
    )
    try:
        result = _run()
        assert result.returncode != 0, result.stdout + result.stderr
        assert scratch.name in result.stdout, result.stdout
        assert "no \"Acceptance Standard\" heading" in result.stdout, result.stdout
    finally:
        scratch.unlink()


def test_a_legacy_plan_before_the_cutoff_is_never_flagged() -> None:
    """A plan filed before the cutoff, with no acceptance-standard field either, must never
    red — Ruling 46's "never retro-red-gate a frozen plan". It is counted in the aggregate
    legacy note line, not flagged per-file.
    """
    scratch = PLANS / "2026-08-20-zz-scratch-check28-legacy.md"
    scratch.write_text(
        "# Scratch plan for check 28's legacy exemption\n\n"
        "**Goal:** exercise the pre-cutoff case — dated before 2026-08-31.\n\n"
        "## Global Constraints\n\nNone.\n",
        encoding="utf-8",
    )
    try:
        result = _run()
        assert result.returncode == 0, result.stdout + result.stderr
        assert "All checks passed" in result.stdout, result.stdout
        assert scratch.name not in result.stdout, result.stdout
    finally:
        scratch.unlink()


def test_a_conforming_plan_after_the_cutoff_is_not_flagged() -> None:
    """The positive control: a plan dated on/after the cutoff that *does* carry a populated
    "Acceptance Standard" heading must pass. Without this case the two tests above could
    both go green by a check that exempts everything, or reds every plan-kind file
    regardless of content.
    """
    scratch = PLANS / "2026-08-31-zz-scratch-check28-conforming.md"
    scratch.write_text(
        "# Scratch plan for check 28's positive control\n\n"
        "**Goal:** exercise the conforming case.\n\n"
        "## Acceptance Standard\n\n"
        "This plan is accepted when:\n\n1. Check 28 passes on this file.\n",
        encoding="utf-8",
    )
    try:
        result = _run()
        assert result.returncode == 0, result.stdout + result.stderr
        assert "All checks passed" in result.stdout, result.stdout
        assert scratch.name not in result.stdout, result.stdout
    finally:
        scratch.unlink()


def test_a_bare_heading_with_no_content_is_refused() -> None:
    """An "Acceptance Standard" heading immediately followed by another heading — nothing
    under it — is "implied", not "actually defined" (`delivery-process.md` §5 step 4), and
    must still red even though the heading text itself is present.
    """
    scratch = PLANS / "2026-08-31-zz-scratch-check28-bare-heading.md"
    scratch.write_text(
        "# Scratch plan for check 28's bare-heading case\n\n"
        "## Acceptance Standard\n\n"
        "## Global Constraints\n\nNone.\n",
        encoding="utf-8",
    )
    try:
        result = _run()
        assert result.returncode != 0, result.stdout + result.stderr
        assert scratch.name in result.stdout, result.stdout
        assert "has no content before the next heading" in result.stdout, result.stdout
    finally:
        scratch.unlink()
