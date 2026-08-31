#!/usr/bin/env python3
"""Register grammar linter — enforces `docs/audit/register.md`'s own Decision-cell grammar.

Ordered by Ruling 50 (`docs/plans/2026-08-30-nt-0015-q1-q5-rulings.md`), which found that
Ruling 46's mechanism (a filename-date cutoff) has no analogue for a register row — a row
carries no date and is edited in place as its normal operation — so the answer here is not
a flag day or a legacy class but conforming the corpus once (Ruling 49's PR) and red-gating
every row from day one. **No cutoff constant, no warn level, no per-row exemption**: this
file must not grow one, ever — a check whose verdict depends on the calendar or on a hand-
maintained finding-id allowlist cannot be reproduced in a fresh clone (Ruling 50 §2).

Three rules, each an obligation the register's own header (`docs/audit/register.md`,
corrected by Ruling 49's Text A/B/C) states in prose:

  1. **Decision-cell grammar.** A Decision cell opens with one of: the register's own
     disposition vocabulary (`fix before close`, `accept`, `carry forward`,
     `split verdict`), `CLAUDE.md` §13's four verdicts (`delivered but untested`,
     `deferred with an owner`, `reassigned`, `not started` — binding, may not be linted
     away), or the negated form F37/F40 need (`fix before close is not available` /
     `is not required` — already a `fix before close` prefix, so no separate branch is
     needed). A cell whose *opening* — emphasis stripped — is a bare status marker
     (`resolved …`, `Fixed —`) is a documented, separate case — Ruling 50 §1 classifies it
     "not a grammar gap" and defers the actual fix to a future status field (P4) — so it is
     excluded from *this* rule and checked instead by rule 2. Anything else is a grammar
     violation.
  2. **Resolution-annotation format.** Every cell rule 1 excluded as a status opening
     (`_opens_with_status` — the *same* predicate, not a second one that could drift from
     the first) must carry a date (`YYYY-MM-DD`) and a PR/commit/doc reference — the content
     Ruling 49's Text A requires ("naming the PR or commit that discharged it"). Sharing one
     predicate between the exclusion and the trigger closes a real gap: an earlier version
     excluded on the bare opening in rule 1 but triggered rule 2 only on a markdown-emphasis
     regex, so an unemphasised `Fixed - ...` opening with no date and no reference was
     excluded by rule 1 and never reached by rule 2 — `lint_register()` returned `[]` for it.
  3. **Unowned-row decay.** Wherever a Decision cell says `unowned` (bare, `unowned by
     design`, or `unowned-pending-authorisation`), the cell must say more than the bare
     disposition — Ruling 49's Text B requires it to "name the event that next confirms or
     assigns its owner," and a cell that stops right after the word names nothing. This is
     a length proxy for "says something," not a semantic parse of what was said.

Plus a structural rule the parser needs to keep working at all: **every data row must split
into exactly 5 fields** (Finding id, Concerns, Work item, Phase, Decision). Two rows failed
this before Ruling 49's PR (F27, F49 — an unescaped literal `|`); nothing prevented a new one
until this check existed.

**Scope.** `docs/audit/phases/1b/register.md` is excluded **by name**, not by date (Ruling
50 §2: it is a closed-phase record, out of scope regardless of when this check runs). A
future phase-2 register is in scope from the commit that creates it, which means adding its
path to `TARGETS` below by hand when that day comes — never inferring it from a glob, which
would silently reach into `phases/1b` too.

Usage: `python3 scripts/register-lint.py` (exit 1 on any violation), or import
`lint_register(path)` — used by `scripts/audit-docs.py` check 29 so this ships inside the
one gate command everyone already runs, without a second gate-command impact-matrix row
(precedent: checks 25-28).
"""
from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent

# Deliberately explicit, never a glob — see "Scope" above. `docs/audit/phases/1b/register.md`
# is NOT here, by name, per Ruling 50 §2.
TARGETS = [REPO / "docs" / "audit" / "register.md"]

DISPOSITIONS = ("fix before close", "accept", "carry forward", "split verdict")
# CLAUDE.md §13's four verdicts — binding, may not be linted away (Ruling 50 §2).
VERDICTS = ("delivered but untested", "deferred with an owner", "reassigned", "not started")
STATUS_PREFIXES = ("resolved", "fixed")

_SEP_ROW = re.compile(r"^\|\s*-+\s*\|")
_EMPHASIS = re.compile(r"^[\*_`\s]+")
_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
_PR_OR_SHA_OR_DOC = re.compile(
    r"PR\s*#\d+|`[0-9a-f]{7,40}`|`docs/[^`]+`|`\.claude/[^`]+`", re.IGNORECASE
)
_UNOWNED = re.compile(r"\bunowned\b", re.IGNORECASE)
# The proxy for "names the event" — a cell long enough to say more than the bare
# disposition + "unowned" is presumed to name something; a bare stop is presumed not to.
_UNOWNED_MIN_LEN = 40


class Row:
    __slots__ = ("fields", "finding_id", "line_no", "raw")

    def __init__(self, finding_id: str, fields: list[str], line_no: int, raw: str) -> None:
        self.finding_id = finding_id
        self.fields = fields
        self.line_no = line_no
        self.raw = raw


def _split_row(line: str) -> list[str]:
    """Split a markdown table row on unescaped `|`, restoring escaped `\\|` afterwards."""
    placeholder = "\x00"
    tmp = line.replace("\\|", placeholder)
    fields = [f.strip() for f in tmp.strip().strip("|").split("|")]
    return [f.replace(placeholder, "\\|") for f in fields]


def parse_register(path: pathlib.Path) -> tuple[list[Row], list[str]]:
    """Parse the register's data rows. Returns (rows, structural-problems).

    A structural problem is a row that does not split into exactly 5 fields — the pipe
    defect Ruling 49's PR fixed by hand (F27, F49) and nothing prevented from recurring
    until this parser existed.
    """
    rows: list[Row] = []
    problems: list[str] = []
    text = path.read_text(encoding="utf-8")
    in_table = False
    for i, line in enumerate(text.splitlines(), start=1):
        if not line.startswith("|"):
            in_table = False
            continue
        if _SEP_ROW.match(line):
            in_table = True
            continue
        if "Finding id" in line and "Decision" in line:
            in_table = True
            continue
        if not in_table:
            continue
        fields = _split_row(line)
        if len(fields) != 5:
            problems.append(
                f"{path.name}:{i}: row splits into {len(fields)} fields, not 5 "
                f"(a literal `|` inside a cell needs `\\|`) — {fields[0][:60]!r}"
            )
            continue
        rows.append(Row(fields[0], fields, i, line))
    return rows, problems


def _strip_emphasis(cell: str) -> str:
    return _EMPHASIS.sub("", cell).strip()


def _opens_with_status(decision: str) -> bool:
    """True when the Decision cell's own **opening** — emphasis stripped — is a status
    marker (`resolved …`, `Fixed —`).

    This is the single predicate rule 1 excludes on and rule 2 triggers on — one test used
    twice, never two written separately that happen to agree today. That drift was a real,
    proven bug: an earlier version excluded on this opening-based test in rule 1 but
    triggered rule 2 on a narrower, markdown-emphasis-only regex, so a bare, unemphasised
    `Fixed - undocumented status change, no date, no ref` was excluded by rule 1 (correctly
    — a status opening isn't a grammar violation) and never reached by rule 2 either (the
    emphasis regex didn't match) — `lint_register()` returned `[]` for a row carrying
    neither a date nor a reference. Sharing this one predicate closes that gap: anything
    rule 1 lets through as "not a grammar question" is exactly what rule 2 must then check.
    """
    opening = _strip_emphasis(decision).lower()
    return any(opening.startswith(s) for s in STATUS_PREFIXES)


def check_decision_grammar(row: Row) -> str | None:
    decision = row.fields[4]
    opening = _strip_emphasis(decision).lower()
    if any(opening.startswith(d) for d in DISPOSITIONS):
        return None
    if any(opening.startswith(v) for v in VERDICTS):
        return None
    if _opens_with_status(decision):
        # Rule 1 does not judge this cell — rule 2 does (same predicate, see
        # `_opens_with_status`). Ruling 50 §1 classifies this class "not a grammar gap";
        # the actual fix is a future status field (P4).
        return None
    return (
        f"{row.finding_id}: Decision cell opens with {decision[:60]!r}, which matches "
        "none of: the register's disposition vocabulary (fix before close / accept / "
        "carry forward / split verdict), CLAUDE.md §13's four verdicts, or a resolution "
        "marker (resolved / Fixed)"
    )


def check_resolution_annotation(row: Row) -> str | None:
    decision = row.fields[4]
    if not _opens_with_status(decision):
        return None
    has_date = bool(_DATE.search(decision))
    has_ref = bool(_PR_OR_SHA_OR_DOC.search(decision))
    if has_date and has_ref:
        return None
    missing = []
    if not has_date:
        missing.append("a date (YYYY-MM-DD)")
    if not has_ref:
        missing.append("a PR/commit/doc reference (`PR #n`, a backtick-quoted SHA, or a "
                        "backtick-quoted docs/ or .claude/ path)")
    return (
        f"{row.finding_id}: carries a resolution marker but no {' and no '.join(missing)} "
        "(Ruling 49 Text A: a resolution annotation must name the PR or commit that "
        "discharged it)"
    )


def check_unowned_decay(row: Row) -> str | None:
    decision = row.fields[4]
    if not _UNOWNED.search(decision):
        return None
    if len(decision.strip()) >= _UNOWNED_MIN_LEN:
        return None
    return (
        f"{row.finding_id}: Decision cell says 'unowned' and stops ({decision.strip()!r}) "
        "— Ruling 49 Text B requires it to name the event that next confirms or assigns "
        "its owner, or it decays to the next CLAUDE.md §14 plan review"
    )


def lint_register(path: pathlib.Path) -> list[str]:
    rows, problems = parse_register(path)
    failures = list(problems)
    for row in rows:
        for check in (check_decision_grammar, check_resolution_annotation, check_unowned_decay):
            msg = check(row)
            if msg:
                failures.append(msg)
    return failures


def main() -> int:
    all_failures: list[str] = []
    for target in TARGETS:
        if not target.exists():
            print(f"skip: {target} does not exist")
            continue
        failures = lint_register(target)
        if failures:
            print(f"{target}: {len(failures)} violation(s)")
            for f in failures:
                print(f"  - {f}")
        else:
            print(f"{target}: OK (0 violations)")
        all_failures.extend(failures)
    if all_failures:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
