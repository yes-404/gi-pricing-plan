"""`scripts/register-lint.py` — the register grammar linter Ruling 50 ordered.

Ruling 50 (`docs/plans/2026-08-30-nt-0015-q1-q5-rulings.md`) found that nothing enforced
`docs/audit/register.md`'s own Decision-cell grammar, ruled "no legacy class, no exemption,
no warn phase, no flag day," and required the check to be red on the first day it lands if
the live register does not conform, and green if it does. `CLAUDE.md` §13: "a check that has
never printed a failure has not been tested" — so this suite proves each of the three rules
red on input built to violate exactly that rule, and proves the live register green as the
control without which any of the three could go green by exempting everything.

No `@pytest.mark.req` marker: this is correctness of the audit tool itself, not evidence for
a numbered platform requirement — the same reasoning `tests/test_scope_audit.py` and
`tests/test_audit_docs_finding_citations.py` give for their own scripts.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
from typing import cast

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "register-lint.py"
AUDIT_SCRIPT = ROOT / "scripts" / "audit-docs.py"
REGISTER = ROOT / "docs" / "audit" / "register.md"

_spec = importlib.util.spec_from_file_location("_register_lint_under_test", SCRIPT)
assert _spec is not None
assert _spec.loader is not None
register_lint = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(register_lint)


def _table(decision: str, finding: str = "X (F999998)") -> str:
    """One well-formed data row wrapped in a minimal, otherwise-conforming table."""
    header = "| Finding id | Concerns | Work item | Phase | Decision |\n|---|---|---|---|---|\n"
    return header + f"| {finding} | concerns | W1 | 1 | {decision} |\n"


def _lint(tmp_path: pathlib.Path, content: str) -> list[str]:
    f = tmp_path / "register.md"
    f.write_text(content, encoding="utf-8")
    return cast("list[str]", register_lint.lint_register(f))


# --- Rule 1: Decision-cell grammar -----------------------------------------------------

def test_a_decision_outside_the_grammar_is_refused(tmp_path: pathlib.Path) -> None:
    """A Decision cell that is not one of the register's own disposition words, CLAUDE.md
    §13's four verdicts, or a resolution marker must fail — this is the failure mode Text C
    (Ruling 49) exists to name: a free-text opening invents a sixth disposition.
    """
    failures = _lint(tmp_path, _table("TBD, someone should look at this."))
    assert failures, "a non-grammar Decision cell must be refused"
    assert "F999998" in failures[0]
    assert "matches none of" in failures[0]


def test_the_four_claude_md_13_verdicts_are_accepted(tmp_path: pathlib.Path) -> None:
    """CLAUDE.md §13's verdicts are binding and 'may not be linted away by a register-local
    vocabulary' (Ruling 50 §2) — a grammar that reds F53/F54's own openings would be a
    register check overruling CLAUDE.md.
    """
    for verdict in (
        "delivered but untested", "deferred with an owner", "reassigned", "not started",
    ):
        failures = _lint(tmp_path, _table(f"**{verdict}** — reason"))
        assert failures == [], f"{verdict!r} must be accepted, got {failures}"


def test_the_negated_fix_before_close_shape_is_accepted(tmp_path: pathlib.Path) -> None:
    """The negated form F37/F40 need — 'is not available' / 'is not required' — is part of
    the grammar's union (Ruling 50 §2), not an outsider.
    """
    for cell in (
        "fix before close is not available — this is a spec amendment first",
        "fix before close is not required — no shipped behaviour is affected",
    ):
        assert _lint(tmp_path, _table(cell)) == []


def test_a_bare_pipe_broken_row_is_refused(tmp_path: pathlib.Path) -> None:
    """A literal `|` inside a cell, unescaped, splits the row into more than 5 fields — the
    defect Ruling 49's PR fixed by hand in F27 and F49. Nothing prevented a new one before
    this check existed.
    """
    content = (
        "| Finding id | Concerns | Work item | Phase | Decision |\n|---|---|---|---|---|\n"
        "| X (F999997) | a | b | c | carry forward | with a stray | pipe |\n"
    )
    f = tmp_path / "register.md"
    f.write_text(content, encoding="utf-8")
    failures = register_lint.lint_register(f)
    assert failures, "an unescaped `|` must be refused, not silently mis-parsed"
    assert "splits into" in failures[0]


# --- Rule 2: resolution-annotation format -----------------------------------------------

def test_a_resolution_marker_with_no_date_or_reference_is_refused(tmp_path: pathlib.Path) -> None:
    """Ruling 49 Text A: a resolved row is annotated in place, 'naming the PR or commit that
    discharged it.' A bare '*resolved*' with neither a date nor a PR/commit/doc reference
    names nothing.
    """
    failures = _lint(tmp_path, _table("*resolved — fixed it, done.*"))
    assert failures, "a resolution marker with no date and no reference must be refused"
    assert "F999998" in failures[0]
    assert "no a date" in failures[0] or "no a PR" in failures[0]


def test_an_unemphasised_status_opening_with_no_date_or_reference_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """Regression for a proven bypass, not a theoretical one.

    An earlier version excluded a status opening from rule 1 on the bare `STATUS_PREFIXES`
    test (no emphasis required) but only triggered rule 2 on a markdown-emphasis-only regex
    (`*resolved`, `**Fixed**`). A new row opening `Fixed - ...` with *no* emphasis was
    excluded by rule 1 (correctly — a status opening is not a grammar violation) and never
    reached by rule 2 either, so `lint_register()` returned `[]` for a row carrying neither a
    date nor a reference. This is the auditor's exact synthetic row that found the hole.
    Both rules now share one predicate (`_opens_with_status`) precisely so this cannot recur.
    """
    cell = "Fixed - undocumented status change, no date, no ref"
    failures = _lint(tmp_path, _table(cell))
    assert failures, "an unemphasised status opening with no date/reference must be refused"
    assert "F999998" in failures[0]
    assert "no a date" in failures[0] or "no a PR" in failures[0]


def test_a_well_formed_resolution_annotation_is_accepted(tmp_path: pathlib.Path) -> None:
    for cell in (
        "*resolved 2026-08-28 (PR #302) — the fix landed.*",
        "**Fixed** — see `5b82b18` — landed 2026-08-29.",
        "***Resolved 2026-08-30*** — see `docs/plans/2026-08-30-example.md`.",
    ):
        assert _lint(tmp_path, _table(cell)) == [], cell


def test_resolved_used_in_prose_about_something_else_is_not_a_false_positive(
    tmp_path: pathlib.Path,
) -> None:
    """'resolved'/'fixed' occurring in ordinary prose — not markdown-emphasised at the word
    itself — must not be mistaken for this row's own resolution annotation. Two real register
    rows (F26, F45) tripped an earlier, cruder version of this check on exactly this shape.
    """
    cell = (
        "carry forward — unowned, needs its own authorisation. Recorded rather than "
        "fixed because the remedy is wide."
    )
    assert _lint(tmp_path, _table(cell)) == []


# --- Rule 3: unowned-row decay -----------------------------------------------------------

def test_a_bare_unowned_row_naming_no_event_is_refused(tmp_path: pathlib.Path) -> None:
    """Ruling 49 Text B: an unowned row must name the event that next confirms or assigns
    its owner, or it decays to the next CLAUDE.md §14 plan review. A cell that says
    'unowned' and stops names nothing.
    """
    failures = _lint(tmp_path, _table("carry forward — unowned."))
    assert failures, "a bare 'unowned' with nothing further must be refused"
    assert "F999998" in failures[0]
    assert "names nothing" in failures[0] or "next confirms" in failures[0]


def test_an_unowned_row_with_a_named_trigger_is_accepted(tmp_path: pathlib.Path) -> None:
    cell = (
        "carry forward with a trigger (a named exposure-ordered reader), unowned by design"
    )
    assert _lint(tmp_path, _table(cell)) == []


# --- Control: the live register must pass, on the tree this check lands on -------------

def test_the_live_register_passes() -> None:
    """Ruling 50 §3: 'the live register at the tree the check lands on must pass, reported
    with that tree.' Without this control, a linter that exempted everything would also show
    green on the three failing fixtures above — this is the case that makes the check's
    passes mean something.
    """
    failures = register_lint.lint_register(REGISTER)
    assert failures == [], failures


def test_check_29_is_wired_into_the_docs_gate() -> None:
    """`scripts/audit-docs.py` runs `register_lint.lint_register` as check 29 (precedent:
    checks 25-28 all landed inside the one gate command rather than as separate scripts) —
    so `python3 scripts/audit-docs.py` alone is proof the register still conforms, with no
    second command for CI or a developer to remember to run.
    """
    result = subprocess.run(
        ["python3", str(AUDIT_SCRIPT)], capture_output=True, text=True, cwd=ROOT
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "check 29" in result.stdout, result.stdout
