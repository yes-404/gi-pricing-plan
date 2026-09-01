#!/usr/bin/env python3
"""Print every open `docs/audit/register.md` row owed by, or blocking, a named close.

Ordered by NT-0015 P5 (`docs/notes/0015-the-register-is-a-ledger-evidence-is-a-file.md`
§2), which exists to replace an owed list compiled by hand at the moment of highest load —
F41, verbatim: the W11 close's hand-compiled list "already runs to thirteen items — a list
that lost NFR-RATE-13/14 for two workstreams even though a register row, F-W9-1, existed for
them the whole time." F-W9-1's own Work item column reads `W9-3`; its Decision column names
"the W11 scoring workstream" as the actual owner. **That gap is why this script searches
both the Work item and Decision columns, not the Work item column alone** — a search
restricted to Work item would repeat F41's exact mistake.

**Ruling 52** (`docs/plans/2026-08-30-nt-0015-q1-q5-rulings.md`) binds this script's output
form:

  1. The output names the command and the **committed revision** it ran against — a SHA on
     `main` or a named branch range, never a bare date and never a dirty worktree, because
     the register amends several times a day and "the register at a date" is not a
     resolvable object. **Enforced, not documented**: this script refuses to run if
     `docs/audit/register.md` has an uncommitted diff (`_dirty_register`).
  2. The output lands verbatim in a closure record as a fenced, explicitly-generated
     evidence block — and it is **not** the record's own findings-and-resolutions table,
     which stays hand-written (`.claude/skills/close-workstream` and the checklists carry
     this; this script only emits the block).
  3. The block is evidence, not authority — where it and a closure record's own table
     disagree, one or the other is amended, never silently (`CLAUDE.md` §0).

Reuses `scripts/register-lint.py`'s row parser and its status-marker predicates rather than
writing a second parser or a second "is this resolved" test — a shape parsed twice
diverges, and a diverged parser here would mean an owed list that silently disagrees with
the linter about what a row is.

**Scope: `docs/audit/register.md` only**, the same exclusion `register-lint.py` states by
name for `docs/audit/phases/1b/register.md` (Ruling 50 §2: a closed-phase record, out of
scope regardless of when a check runs, named rather than dated so the exclusion stays
visible). This script does not read a second-path constant at all — `REGISTER` is a single
hardcoded path — so the exclusion holds by construction, not by an added check. A future
phase-2 register would need this file taught a second target the same way `register-lint.py`
would need one; neither exists yet, so nothing here reaches into `phases/1b`.

**Matching modes**, chosen from the single positional argument:

  - `review` — rows whose Decision column names the `CLAUDE.md` §14 plan review as an
    owner or a decay target. Detected by the literal substring `§14` (every row that
    explicitly assigns itself to that review quotes it — see the register's own P2 decay
    sentence and F26/F29/F31/F33/F52/F61). This is a **textual proxy**, not a semantic
    parse of "no other event was named" — a truly bare unowned row with no named event at
    all would already fail `register-lint.py` rule 3, so at the tree this script runs
    against, an unowned row always names something, and `review` mode only catches the
    rows that name *this* event, in these words. Flagged in the P5 report as a judgement
    call, not a derived fact.
  - a **phase id** (`1a`, `1b`, `2`, `3`, `4`, …: matches `^[0-9][0-9a-zA-Z]*$`) — rows
    whose Phase column, split on `/` (a row can span several phases, e.g. `2/3/4`), names
    that phase.
  - anything else — a **work-item id** (`W11`, `W10-2`, `W6b-14`, `nt-0010-0011-adoption`,
    …), matched case-insensitively at a word boundary against the Work item column *and*
    the Decision column, so an owner named only in prose (F-W9-1's shape) is still found.

**Resolved rows.** A row whose Decision cell *opens* with a resolution marker
(`register_lint._opens_with_status`, the same predicate `register-lint.py` rule 1 excludes
on) is treated as closed and left out of the owed list — reusing that one predicate, not a
second "is this resolved" test. A row carrying only an *appended*, mid-cell resolution
marker (`register_lint._STATUS_MARKER` — the F50/F51 shape: opens with a disposition,
discharged later in the same cell) is **not** auto-excluded: distinguishing "fully
superseded" from "partially superseded" inside one cell needs the judgement P4's own status
field exists to make mechanical, and this script would rather over-report a closed row than
silently drop an open one. Every row excluded as opening-with-status is still named, in a
second section of the output, so a reader can catch a wrongly-excluded row rather than
lose it silently — the register's header names five rows (F-W10-1-1, F-W10-2-1,
F-W10-2-2, F32, F28) where a status marker and further carried content share one cell, and
F28 is exactly this: it opens `**Fixed**` and still carries P5, P7, P12 and P1b's
working-note half. Excluding it outright would be this script's own F41.

Usage: `python3 scripts/register-owed.py <work-id | phase | review>`
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REGISTER = REPO / "docs" / "audit" / "register.md"

_spec = importlib.util.spec_from_file_location(
    "_register_lint", REPO / "scripts" / "register-lint.py"
)
assert _spec is not None
assert _spec.loader is not None
register_lint = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(register_lint)

_PHASE_ID = re.compile(r"^[0-9][0-9a-zA-Z]*$")
_REVIEW_MARKER = re.compile(r"§14")


class Match:
    """One matched row, tagged with whether it was excluded as a resolved row. A plain
    class rather than `@dataclass` — a dataclass's string-annotation resolution looks up
    `sys.modules[cls.__module__]`, which is `None` for a module loaded via
    `importlib.util.module_from_spec` and never registered in `sys.modules` (exactly how
    this script imports `register-lint.py`, and how its own tests import this file), and
    fails with an opaque `AttributeError` rather than a useful one.
    """

    __slots__ = ("excluded_resolved", "row")

    def __init__(self, row: register_lint.Row, excluded_resolved: bool) -> None:
        self.row = row
        self.excluded_resolved = excluded_resolved


def _word_boundary(token: str) -> re.Pattern[str]:
    return re.compile(r"\b" + re.escape(token) + r"\b", re.IGNORECASE)


def _is_resolved(decision: str) -> bool:
    """A row this script treats as fully closed: its Decision cell *opens* with a
    resolution marker. Reuses `register_lint._opens_with_status` — the same predicate
    `register-lint.py` rule 1 excludes on — rather than a second, possibly-diverging test.
    """
    return bool(register_lint._opens_with_status(decision))


def _matches_phase(row: register_lint.Row, phase: str) -> bool:
    cell = row.fields[3]
    parts = [p.strip().lower() for p in cell.split("/")]
    return phase.lower() in parts


def _matches_work_id(row: register_lint.Row, work_id: str) -> bool:
    pattern = _word_boundary(work_id)
    work_item, decision = row.fields[2], row.fields[4]
    return bool(pattern.search(work_item) or pattern.search(decision))


def _matches_review(row: register_lint.Row) -> bool:
    return bool(_REVIEW_MARKER.search(row.fields[4]))


def select_matches(
    rows: list[register_lint.Row], target: str
) -> list[Match]:
    """Every row matching `target`'s mode, each tagged with whether it was excluded as
    resolved. Callers filter on `excluded_resolved` to get the owed list versus the
    reviewable-exclusions list; nothing here silently drops a matched row.
    """
    if target.lower() == "review":
        predicate = _matches_review
    elif _PHASE_ID.match(target):
        predicate = lambda row: _matches_phase(row, target)  # noqa: E731
    else:
        predicate = lambda row: _matches_work_id(row, target)  # noqa: E731

    matches: list[Match] = []
    for row in rows:
        if predicate(row):
            matches.append(Match(row=row, excluded_resolved=_is_resolved(row.fields[4])))
    return matches


def _mode_label(target: str) -> str:
    if target.lower() == "review":
        return "review (rows naming the CLAUDE.md §14 plan review)"
    if _PHASE_ID.match(target):
        return f"phase {target!r}"
    return f"work item {target!r}"


def _dirty_path(repo: Path, path: Path) -> str | None:
    """None if `path` (inside `repo`) has no uncommitted diff; otherwise a message naming
    why this script refuses to run (Ruling 52 constraint 1, enforced not documented: never
    cite a dirty worktree as though it were a committed revision). A pure function of its
    two arguments so it can be proven against a throwaway git repo, not only the real one.
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--", str(path.relative_to(repo))],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        return f"could not run `git status` against {repo}: {exc}"
    if result.stdout.strip():
        return (
            f"{path} has an uncommitted diff:\n{result.stdout}"
            "\nRuling 52 forbids citing a dirty worktree as the tree an owed list ran "
            "against — commit or stash the register first."
        )
    return None


def _dirty_register(repo: Path) -> str | None:
    return _dirty_path(repo, REGISTER)


def _revision(repo: Path) -> str:
    """The committed revision to cite: the current branch name if HEAD is on one, else the
    short SHA alone (still a resolvable, committed object either way).
    """
    sha = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=repo, capture_output=True, text=True, check=True,
    ).stdout.strip()
    branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=repo, capture_output=True, text=True, check=True,
    ).stdout.strip()
    if branch and branch != "HEAD":
        return f"{sha} (`{branch}`)"
    return f"{sha} (detached)"


def render(target: str, matches: list[Match], revision: str, command: str) -> str:
    owed = [m for m in matches if not m.excluded_resolved]
    excluded = [m for m in matches if m.excluded_resolved]
    lines = [
        f"Generated by `{command}` against `{revision}`.",
        f"Mode: {_mode_label(target)}. {len(owed)} owed row(s), {len(excluded)} matched but "
        "excluded as opening with a resolution marker (listed below — verify none carries a "
        "residual item; the register's own header names five rows where a status marker and "
        "further carried content share one cell).",
        "",
    ]
    if owed:
        for m in owed:
            lines.append(f"- **{m.row.finding_id}** (work item: {m.row.fields[2]!r}, phase: "
                          f"{m.row.fields[3]!r}) — {m.row.fields[4]}")
    else:
        lines.append("(none)")
    if excluded:
        lines.append("")
        lines.append("Excluded as opening with a resolution marker — verify:")
        for m in excluded:
            lines.append(f"- {m.row.finding_id}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("target", help="a work-item id, a phase id, or the literal 'review'")
    args = parser.parse_args(argv)

    dirty = _dirty_register(REPO)
    if dirty is not None:
        print(f"refused: {dirty}", file=sys.stderr)
        return 2

    rows, problems = register_lint.parse_register(REGISTER)
    if problems:
        print("refused: register.md has structural problems register-lint.py would also "
              "reject:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 2

    matches = select_matches(rows, args.target)
    revision = _revision(REPO)
    command = f"python3 scripts/register-owed.py {args.target}"
    print(render(args.target, matches, revision, command))
    return 0


if __name__ == "__main__":
    sys.exit(main())
