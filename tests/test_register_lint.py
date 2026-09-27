"""`scripts/register-lint.py` — the register grammar linter RL-910 ordered.

RL-910 (`docs/rulings/RL-00910-q2-rl-906-s-mechanism-does-not-transfer-its-principle-does-and-the-answer-here-is-to-conform-the-corpus-and-red-gate-from-day-one.md`) found that nothing enforced
`docs/findings/register.md`'s own Decision-cell grammar, ruled "no legacy class, no exemption,
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
    return header + f"| {finding} | concerns | WK-657 | 1 | {decision} |\n"


def _lint(tmp_path: pathlib.Path, content: str) -> list[str]:
    f = tmp_path / "register.md"
    f.write_text(content, encoding="utf-8")
    return cast("list[str]", register_lint.lint_register(f))


# --- Rule 1: Decision-cell grammar -----------------------------------------------------

def test_a_decision_outside_the_grammar_is_refused(tmp_path: pathlib.Path) -> None:
    """A Decision cell that is not one of the register's own disposition words, CLAUDE.md
    §13's four verdicts, or a resolution marker must fail — this is the failure mode Text C
    (RL-909) exists to name: a free-text opening invents a sixth disposition.
    """
    failures = _lint(tmp_path, _table("TBD, someone should look at this."))
    assert failures, "a non-grammar Decision cell must be refused"
    assert "F999998" in failures[0]
    assert "matches none of" in failures[0]


def test_the_four_claude_md_13_verdicts_are_accepted(tmp_path: pathlib.Path) -> None:
    """CLAUDE.md §13's verdicts are binding and 'may not be linted away by a register-local
    vocabulary' (RL-910 §2) — a grammar that reds F53/F54's own openings would be a
    register check overruling CLAUDE.md.
    """
    for verdict in (
        "delivered but untested", "deferred with an owner", "reassigned", "not started",
    ):
        failures = _lint(tmp_path, _table(f"**{verdict}** — reason"))
        assert failures == [], f"{verdict!r} must be accepted, got {failures}"


def test_the_negated_fix_before_close_shape_is_accepted(tmp_path: pathlib.Path) -> None:
    """The negated form F37/F40 need — 'is not available' / 'is not required' — is part of
    the grammar's union (RL-910 §2), not an outsider.
    """
    for cell in (
        "fix before close is not available — this is a spec amendment first",
        "fix before close is not required — no shipped behaviour is affected",
    ):
        assert _lint(tmp_path, _table(cell)) == []


def test_a_bare_pipe_broken_row_is_refused(tmp_path: pathlib.Path) -> None:
    """A literal `|` inside a cell, unescaped, splits the row into more than 5 fields — the
    defect RL-909's PR fixed by hand in F27 and F49. Nothing prevented a new one before
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
    """RL-909 Text A: a resolved row is annotated in place, 'naming the PR or commit that
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


def test_an_appended_resolution_with_no_reference_is_refused(tmp_path: pathlib.Path) -> None:
    """Regression for a second, real gap the fix for the first one nearly introduced.

    Making rule 2 trigger only on `_opens_with_status` (rule 1's exclusion test) would have
    been a *replacement* of the old trigger, not an *extension* of it — and the old trigger
    (`_STATUS_MARKER`, searched anywhere in the cell) covered a shape `_opens_with_status`
    structurally cannot see: a row that opens with a disposition/verdict and is discharged
    later, appended in place, when the finding lands. F50 and F51 are exactly this shape —
    `carry forward, unowned. … ***Resolved 2026-08-30*** — RL-922 §7 assigned the fix …` —
    and it is the *common* discharge shape here, not an edge case. Built from that real form,
    with the reference stripped out, rather than a minimal string.
    """
    cell = (
        "carry forward, unowned. Fix is a docstring correction restating the true safety "
        "argument. ***Resolved 2026-08-30*** — the fix landed."
    )
    failures = _lint(tmp_path, _table(cell))
    assert failures, "an appended resolution with no reference must be refused"
    assert "F999998" in failures[0]
    assert "no a PR" in failures[0]


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
    """RL-909 Text B: an unowned row must name the event that next confirms or assigns
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


# --- Rows across a blank line ------------------------------------------------------------

def test_a_data_row_after_a_blank_line_is_still_parsed(tmp_path: pathlib.Path) -> None:
    """Regression for a proven bug (found building `register-owed.py`, RFC-896 P5): the live
    register uses blank lines inside its one data table for readability, with no repeated
    header (`docs/findings/register.md` around F52-F61). An earlier `parse_register` reset
    `in_table` on any non-`|` line, including a blank one, and only a fresh separator/header
    row set it back — so every row after the first such blank line was silently dropped, and
    `main()` still printed 'OK (0 violations)' because a dropped row is never checked. This
    is `CLAUDE.md` §13's 'a check that has never printed a failure has not been tested'
    turned inside out: the check printed passing precisely because it had stopped looking.
    Proven directly against the live register at the tree this fix lands on: parsing it finds
    58 rows, not 48 — the ten past the first blank line (F52-F61) were invisible before.
    """
    content = (
        "| Finding id | Concerns | Work item | Phase | Decision |\n"
        "|---|---|---|---|---|\n"
        "| A (F999996) | before the gap | WK-657 | 1 | carry forward — unowned by design, "
        "decays to the next §14 review |\n"
        "\n"
        "| B (F999995) | after the gap | WK-657 | 1 | **not started** — nothing built yet |\n"
    )
    f = tmp_path / "register.md"
    f.write_text(content, encoding="utf-8")
    rows, problems = register_lint.parse_register(f)
    assert [r.finding_id for r in rows] == ["A (F999996)", "B (F999995)"], (
        "the row after the blank line must not be silently dropped"
    )
    # Amended 2026-08-31: the gap is now ALSO a reported problem. Reading past it and
    # accepting it are different things, and the original version of this test asserted
    # `problems == []` — pinning the tolerance as correct behaviour. It was not: GFM ends a
    # table at a blank line, so the live register rendered F52 and then F53-F64 as bare
    # paragraphs for as long as the gaps existed. This check had been taught to read through
    # the one document defect it should have failed on. Both halves are the contract now:
    # every row is still linted, AND the gap is loud.
    assert len(problems) == 1, "the gap must be reported, not silently tolerated"
    assert "split by a non-table line" in problems[0]


def test_a_contiguous_table_reports_no_gap(tmp_path: pathlib.Path) -> None:
    """Positive control for the check above, run against the same code path rather than an
    easier one: an unbroken table of the same shape must report nothing. Without this, a gap
    check that fired on every register — or on none — would look identical in the suite.
    """
    content = (
        "| Finding id | Concerns | Work item | Phase | Decision |\n"
        "|---|---|---|---|---|\n"
        "| A (F999996) | before | WK-657 | 1 | carry forward — unowned by design, "
        "decays to the next §14 review |\n"
        "| B (F999995) | after | WK-657 | 1 | **not started** — nothing built yet |\n"
    )
    f = tmp_path / "register.md"
    f.write_text(content, encoding="utf-8")
    rows, problems = register_lint.parse_register(f)
    assert len(rows) == 2
    assert problems == []


def test_a_row_missing_its_leading_pipe_is_reported_even_as_the_last_line(
    tmp_path: pathlib.Path,
) -> None:
    """GFM makes leading pipes optional, so a contributor can write a row this parser skips
    entirely: `if not line.startswith("|"): continue` fires before `seen` is incremented, so
    the `assert classified == seen` guard — the device that makes every other silent-drop
    class here impossible — cannot see it.

    The first version of the contiguity check bounded its sweep by `rows[-1].line_no`, i.e.
    wherever the field-splitter last SUCCEEDED, and so caught such a row only when a
    well-formed row followed it. The auditor refuted that with this fixture: a hidden row as
    the LAST line was invisible, `problems == []`. That is the position that matters, because
    every finding from F52 on was filed by appending to the end of the table. Both positions
    are pinned here so the bound cannot regress to the parsed-rows one.
    """
    header = (
        "| Finding id | Concerns | Work item | Phase | Decision |\n"
        "|---|---|---|---|---|\n"
    )
    good = (
        "| A (F999996) | before | WK-657 | 1 | carry forward — unowned by design, "
        "decays to the next §14 review |\n"
    )
    hidden = "C (F999994) | no leading pipe | WK-657 | 1 | **not started** — nothing built yet |\n"

    trailing = tmp_path / "trailing.md"
    trailing.write_text(header + good + hidden, encoding="utf-8")
    rows, problems = register_lint.parse_register(trailing)
    assert len(rows) == 1, "the hidden row is still not parsed — that is the residual"
    assert len(problems) == 1, "but it must no longer be SILENT"
    assert "split by a non-table line" in problems[0]

    sandwiched = tmp_path / "sandwiched.md"
    sandwiched.write_text(header + good + hidden + good, encoding="utf-8")
    _, problems = register_lint.parse_register(sandwiched)
    assert len(problems) == 1


def test_prose_and_a_fenced_example_table_below_the_register_are_not_flagged(
    tmp_path: pathlib.Path,
) -> None:
    """The contiguity sweep must stop at the end of the table's own section, not at the last
    four-pipe line anywhere in the file.

    The first bound that fixed the trailing-row case searched the whole file for row-shaped
    lines, so a fenced example table — or a `|`-heavy shell pipeline in prose — appearing
    anywhere below the register dragged the upper bound down to it and flagged every ordinary
    line in between. The auditor built exactly this fixture: 8 problems, 7 of them prose,
    blank lines and a heading that belong to no table.

    A markdown heading cannot occur inside a table, so it terminates the section safely. Both
    bounds are needed: heading alone would flag the prose paragraph that sits between the
    live register's table and `## F42 is retired`, which is why that shape is pinned too.
    """
    header = (
        "| Finding id | Concerns | Work item | Phase | Decision |\n"
        "|---|---|---|---|---|\n"
    )
    good = (
        "| A (F999996) | before | WK-657 | 1 | carry forward — unowned by design, "
        "decays to the next §14 review |\n"
    )

    below = tmp_path / "below.md"
    below.write_text(
        header + good + "\nSome prose about the register.\n\n## Appendix\n\n"
        "```\n| col1 | col2 | col3 | col4 |\n```\n",
        encoding="utf-8",
    )
    _, problems = register_lint.parse_register(below)
    # The one surviving problem is the pre-existing field-count check on the fenced row,
    # which this change neither introduced nor addresses. No contiguity problem at all.
    assert not [p for p in problems if "split by a non-table line" in p]

    live_shape = tmp_path / "live_shape.md"
    live_shape.write_text(
        header + good + "\nA carried finding is written here by the close checklist.\n"
        "\n## F42 is retired\n\nprose\n",
        encoding="utf-8",
    )
    _, problems = register_lint.parse_register(live_shape)
    assert problems == [], "the paragraph between the table and the next heading is not a gap"


def test_the_live_register_table_is_contiguous(tmp_path: pathlib.Path) -> None:
    """The live register must render as one table. This is the corpus check: the unit tests
    above prove the rule, this proves the artifact obeys it. It failed at `567eea2` — two
    blank lines around F52 split the table into three, and everything from F52 on rendered as
    prose in GitHub's view of the file while every check printed OK.
    """
    rows, problems = register_lint.parse_register(register_lint.TARGETS[0])
    assert rows, "the live register parsed to zero rows — the parser, not the register"
    assert problems == [], f"the live register's table is not contiguous: {problems}"


# --- Header detected by position, not by text --------------------------------------------

def test_a_data_row_naming_both_column_headers_is_not_dropped(tmp_path: pathlib.Path) -> None:
    """Regression for a proven bug, found live rather than hypothesised: the header test was
    `"Finding id" in line and "Decision" in line` — a substring match anywhere in the row,
    not a header-position check. An auditor's own draft finding (F64), *about this exact
    parser*, quoted both column names in its Concerns cell and was silently dropped by the
    bug it was describing — no violation, no structural-problem message, nothing in
    `main()`'s output to say a row had vanished. Reworded before it landed, so this fixture
    reconstructs the collision shape rather than quoting the live row.

    `parse_register` now finds the header by **position** — the `|`-led line immediately
    before the delimiter row — so a data row's prose can say anything about the register's
    own columns without being mistaken for one.
    """
    content = (
        "| Finding id | Concerns | Work item | Phase | Decision |\n"
        "|---|---|---|---|---|\n"
        "| Parser drops rows naming its own columns (F964) | `register-lint.py`'s header "
        "test matches any line containing both `Finding id` and `Decision` as substrings, "
        "so a row about this exact bug is itself silently dropped | RFC-896 | 2 | fix "
        "before close — detect the header by position, not by text |\n"
        "| Second, unrelated row (F963) | nothing special | WK-657 | 1 | **not started** |\n"
    )
    f = tmp_path / "register.md"
    f.write_text(content, encoding="utf-8")
    rows, problems = register_lint.parse_register(f)
    assert problems == []
    assert [r.finding_id for r in rows] == [
        "Parser drops rows naming its own columns (F964)",
        "Second, unrelated row (F963)",
    ], "a data row naming both column headers in its own prose must not be dropped"


def test_the_header_row_itself_is_never_parsed_as_data(tmp_path: pathlib.Path) -> None:
    """The position-based header detection must still exclude the real header — this is the
    control for the fix above: a check that only ever adds rows in would pass the collision
    test above by accident if it stopped excluding the header entirely.
    """
    content = (
        "| Finding id | Concerns | Work item | Phase | Decision |\n"
        "|---|---|---|---|---|\n"
        "| A (F962) | concerns | WK-657 | 1 | **not started** |\n"
    )
    f = tmp_path / "register.md"
    f.write_text(content, encoding="utf-8")
    rows, problems = register_lint.parse_register(f)
    assert problems == []
    assert [r.finding_id for r in rows] == ["A (F962)"]


def test_live_register_row_count_matches_a_direct_count(tmp_path: pathlib.Path) -> None:
    """The register's own blank-line gaps (verified above) mean a naive `grep -c '^| F'`-style
    count is not a safe cross-check on its own — but a count of every line that looks like a
    data row (starts with `| ` and is not the header or separator) is, since those are the
    same three lines this parser itself excludes. Catches a future regression where the parser
    drops rows again but by a different mechanism than the blank-line one above.
    """
    text = REGISTER.read_text(encoding="utf-8")
    expected = 0
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        if register_lint._SEP_ROW.match(line):
            continue
        if "Finding id" in line and "Decision" in line:
            continue
        expected += 1
    rows, problems = register_lint.parse_register(REGISTER)
    assert problems == []
    assert len(rows) == expected


# --- Control: the live register must pass, on the tree this check lands on -------------

def test_the_live_register_passes() -> None:
    """RL-910 §3: 'the live register at the tree the check lands on must pass, reported
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


# --- P4: findings-file migration residue (RL-911) ------------------------------------
#
# RL-911 §2: "the residue is measured, in one aggregate line" — "with no such line,
# 'incremental migration' is a claim nothing can falsify." CLAUDE.md §13: "a check that has
# never printed a failure has not been tested" — so this proves the count non-zero on a
# fixture built to need migration, and zero on one that does not, rather than asserting the
# mechanism works from reading the code.

def _rows_of(content: str, tmp_path: pathlib.Path) -> list[object]:
    f = tmp_path / "register.md"
    f.write_text(content, encoding="utf-8")
    rows, problems = register_lint.parse_register(f)
    assert problems == []
    return cast("list[object]", rows)


def test_residue_is_nonzero_when_a_row_exceeds_the_threshold(tmp_path: pathlib.Path) -> None:
    """A deliberately broken input: one row long enough to need a findings-file split, and
    nothing else in the table. The residue count must be exactly 1, not 0 and not silently
    swallowed — the failure mode this line exists to make impossible to miss.
    """
    long_decision = "carry forward — unowned by design, decays to the next §14 review. " + (
        "Forensic evidence padding this cell well past the migration threshold. " * 20
    )
    content = _table(long_decision, finding="Long row (F999994)")
    assert len(content) > register_lint.ROW_LENGTH_THRESHOLD, "fixture must exceed the threshold"
    rows = _rows_of(content, tmp_path)
    over, total = register_lint.residue(rows)
    assert (over, total) == (1, 1)
    line = register_lint.residue_line(tmp_path / "register.md", rows)
    assert "1 of 1" in line
    assert str(register_lint.ROW_LENGTH_THRESHOLD) in line


def test_residue_is_zero_when_every_row_is_short(tmp_path: pathlib.Path) -> None:
    """The control: a table with no row anywhere near the threshold must report a true zero,
    not a count that happens to read as zero because nothing was measured.
    """
    content = _table("**not started** — nothing built yet", finding="Short row (F999993)")
    assert len(content) < register_lint.ROW_LENGTH_THRESHOLD
    rows = _rows_of(content, tmp_path)
    over, total = register_lint.residue(rows)
    assert (over, total) == (0, 1)
    line = register_lint.residue_line(tmp_path / "register.md", rows)
    assert "0 of 1" in line


def test_residue_counts_are_never_treated_as_lint_failures() -> None:
    """An over-threshold row must not, on its own, fail `lint_register` — RL-911: 'never a
    per-row judgement,' and the migration is opportunistic-on-amendment, not mandatory. This
    guards against the residue mechanism accidentally growing into a fourth grammar rule.
    """
    failures = register_lint.lint_register(REGISTER)
    assert failures == [], (
        "no row should fail linting purely for exceeding the migration threshold"
    )


def test_residue_line_reflects_the_live_register(tmp_path: pathlib.Path) -> None:
    """Cross-check against the live register directly, so a change to `ROW_LENGTH_THRESHOLD`
    or to `residue()` that silently stops counting correctly is caught here, not only in the
    executor's own hand-run measurement.
    """
    rows, problems = register_lint.parse_register(REGISTER)
    assert problems == []
    over, total = register_lint.residue(rows)
    assert total == len(rows)
    recomputed_over = sum(1 for r in rows if len(r.raw) > register_lint.ROW_LENGTH_THRESHOLD)
    assert over == recomputed_over


def test_register_lint_main_prints_the_residue_line() -> None:
    """`main()` — the entry point a developer or CI actually runs — must print the residue
    line, not just make it importable. Runs the real subprocess so nothing about pytest's own
    import machinery can hide a wiring mistake in `main()` itself.
    """
    result = subprocess.run(
        ["python3", str(SCRIPT)], capture_output=True, text=True, cwd=ROOT
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "residue —" in result.stdout, result.stdout
    assert str(register_lint.ROW_LENGTH_THRESHOLD) in result.stdout


def test_check_29_note_carries_the_residue_line() -> None:
    """The docs gate itself (not just standalone `register-lint.py`) must surface the residue
    count, per RL-911's 'printed every run' — otherwise a developer who only ever runs
    `audit-docs.py` never sees it.
    """
    result = subprocess.run(
        ["python3", str(AUDIT_SCRIPT)], capture_output=True, text=True, cwd=ROOT
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "residue —" in result.stdout, result.stdout
