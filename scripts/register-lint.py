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
  2. **Resolution-annotation format.** Triggers on the union of two conditions, each closing
     a gap the other cannot: (a) every cell rule 1 excluded as a status opening
     (`_opens_with_status` — the *same* predicate rule 1 uses, not a second one that could
     drift from the first — this is what closes the bare-opening bypass: an earlier version
     excluded `Fixed - ...` in rule 1 but only triggered rule 2 on a markdown-emphasis regex,
     so `lint_register()` returned `[]` for a row with no date and no reference); (b) a cell
     carrying an *emphasised* resolution marker anywhere (`_STATUS_MARKER` — a row that opens
     with a disposition and is discharged later, appended in place, e.g. F50/F51's "carry
     forward, unowned. … `***Resolved 2026-08-30***` — …", which (a) alone cannot see because
     it only looks at the opening). Either way, the cell must carry a date (`YYYY-MM-DD`) and
     a PR/commit/doc reference — the content Ruling 49's Text A requires ("naming the PR or
     commit that discharged it").
  3. **Unowned-row decay.** Wherever a Decision cell says `unowned` (bare, `unowned by
     design`, or `unowned-pending-authorisation`), the cell must say more than the bare
     disposition — Ruling 49's Text B requires it to "name the event that next confirms or
     assigns its owner," and a cell that stops right after the word names nothing. This is
     a length proxy for "says something," not a semantic parse of what was said.

Plus two structural rules the parser needs to keep working at all. **Every data row must
split into exactly 5 fields** (Finding id, Concerns, Work item, Phase, Decision). Two rows
failed this before Ruling 49's PR (F27, F49 — an unescaped literal `|`); nothing prevented a
new one until this check existed. **The header row is found by position** — the `|`-led
line immediately before the delimiter row, never by matching column-name text — because a
text match silently drops any data row whose own prose names both columns; see
`parse_register`'s own comment for the live incident (F64) this replaced.

**P4's addition is not a fourth grammar rule.** `ROW_LENGTH_THRESHOLD` and `residue_line()`
below print one aggregate line, every run, counting rows whose evidence has outgrown the
table and not yet migrated to `docs/audit/findings/<F-id>.md` (Ruling 51) — never a per-row
failure, and no row is ever red-gated for being long.

**Scope.** `docs/audit/phases/1b/register.md` is excluded **by name**, not by date (Ruling
50 §2: it is a closed-phase record, out of scope regardless of when this check runs). A
future phase-2 register is in scope from the commit that creates it, which means adding its
path to `TARGETS` below by hand when that day comes — never inferring it from a glob, which
would silently reach into `phases/1b` too.

Usage: `python3 scripts/register-lint.py` (exit 1 on any violation), or import
`lint_register(path)` — used by `scripts/audit-docs.py` check 29 so this ships inside the
one gate command everyone already runs, without a second gate-command impact-matrix row
(precedent: checks 25-28). `residue_line(path, rows)` is the P4 residue line; check 29
prints it as a note (never a failure) so the docs gate carries it too.
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
# A genuine status annotation is markdown-emphasised at the word itself — `*resolved …*`,
# `**Fixed**`, `***Resolved …***` — never a bare "resolved"/"fixed" occurring in prose about
# something else (e.g. "resolved separately by PR #355", "rather than fixed because …",
# both real register text that is not this row's own resolution). This catches an
# *appended* resolution — a row that opens with a disposition and is discharged later, in
# place, when the finding lands (F50, F51's shape: "carry forward, unowned. … ***Resolved
# 2026-08-30*** — …") — which `_opens_with_status` alone cannot see, because that predicate
# only looks at the cell's opening.
_STATUS_MARKER = re.compile(r"\*{1,3}(resolved|fixed)\b", re.IGNORECASE)
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
    lines = path.read_text(encoding="utf-8").splitlines()

    # The header is identified by **position**, never by text: the `|`-led line
    # immediately before a delimiter row (`|---|---|...`), of which the register's one
    # table has exactly one. An earlier version matched on content instead —
    # `"Finding id" in line and "Decision" in line` — a substring test anywhere in the
    # line, and it silently swallowed any *data* row whose own prose happened to name both
    # columns: no violation, no structural-problem message, no signal of any kind. Found
    # live — an auditor draft finding (F64) *about this exact parser* quoted both column
    # names and was silently dropped by the bug it was describing, before the row was
    # reworded to avoid it. A line's position relative to the delimiter cannot collide
    # with what the line says, the way a text match always can.
    header_lines = {
        i
        for i, line in enumerate(lines)
        if line.startswith("|") and i + 1 < len(lines) and _SEP_ROW.match(lines[i + 1])
    }

    # `in_table` latches on once the header/separator row is seen and is never reset by a
    # blank or prose line — the register's one data table is interrupted by blank lines for
    # readability (e.g. around F52-F61) without a repeated header, and resetting on any
    # non-`|` line silently dropped every row after the first such gap (confirmed: 10 of 58
    # rows, F52-F61, invisible to this check despite `main()` printing "OK (0 violations)").
    # A line that does not start with `|` is simply skipped, never treated as "table over" —
    # safe here because the register's prose sections (after the table) contain no `|`-led
    # lines at all, verified directly rather than assumed.
    in_table = False
    # This function has silently dropped rows three separate times in one day (a strictness
    # mismatch between two rules, the blank-line reset the comment above fixes, and the
    # header-text collision this rewrite fixes) — every one printed "OK (0 violations)".
    # Tallying every `|`-led line into exactly one bucket below turns a fourth such bug into
    # a loud `AssertionError` here rather than another silent one: `seen` counts every line
    # this loop looks at; `classified` is incremented in every branch, with no branch that
    # can `continue` past this accounting uncounted.
    seen = 0
    classified = 0
    for idx, line in enumerate(lines):
        if not line.startswith("|"):
            continue
        seen += 1
        lineno = idx + 1
        if idx in header_lines:
            in_table = True
            classified += 1
            continue
        if _SEP_ROW.match(line):
            in_table = True
            classified += 1
            continue
        if not in_table:
            # Before any table has started. The register's prose carries no `|`-led line
            # (verified above) so this branch is defensive rather than load-bearing today —
            # still tallied, never silently unaccounted for.
            classified += 1
            continue
        fields = _split_row(line)
        if len(fields) != 5:
            problems.append(
                f"{path.name}:{lineno}: row splits into {len(fields)} fields, not 5 "
                f"(a literal `|` inside a cell needs `\\|`) — {fields[0][:60]!r}"
            )
            classified += 1
            continue
        rows.append(Row(fields[0], fields, lineno, line))
        classified += 1
    assert classified == seen, (
        f"{path}: {seen - classified} table-region `|`-led line(s) fell through this "
        "loop's accounting uncounted — the exact silent-row-drop failure this tally exists "
        "to make loud instead"
    )
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
    # A union, not either alone: `_opens_with_status` is rule 1's own exclusion test — the
    # bare-opening bypass closes only if rule 2 checks everything rule 1 excludes.
    # `_STATUS_MARKER` covers the appended-resolution shape (F50, F51: a row opens with a
    # disposition and is discharged later, in place, with "*** Resolved <date> *** — …"
    # partway through the cell) — a case `_opens_with_status` cannot see because it only
    # looks at the opening. Dropping either half reopens a gap the other cannot cover.
    if not (_opens_with_status(decision) or _STATUS_MARKER.search(decision)):
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


# --- P4: findings-file migration residue (Ruling 51, NT-0015) --------------------------
#
# A row's evidence belongs in `docs/audit/findings/<F-id>.md`, per Ruling 53, once it is
# long enough that the table cell is destroying scannability rather than serving as an
# index (NT-0015 motivation item 4). Migration is **never** mandatory outside an
# amendment — Ruling 51 rejects both a bulk sweep (51 rows of judgement-heavy edits is
# the unreviewable diff the register's own F47 row declines for itself) and a "worst
# offenders" slice (measured a class of 23-29 rows, not the two named in the note). So an
# over-threshold row is never a *violation* — no row is ever failed here for being long —
# and this is not a fourth grammar rule. It is one **aggregate** line, printed every run,
# because "incremental migration" is unfalsifiable without it: with no residue count,
# nothing distinguishes an opportunistic rule actually in force from no rule at all
# (Ruling 51 §2). This is the one device that transfers from Ruling 46, which replaced
# 114 per-row warnings with a single aggregate line for the identical reason.
#
# **The threshold is a constant, fixed once from the distribution measured when it was
# written — never a per-row judgement, never a date** (Ruling 51, which forbids exactly
# those two shapes for this constant, the same two `register-lint.py`'s own module
# docstring forbids for the grammar rules above). Measured at the tree this constant was
# added on (`docs/audit/register.md`, 61 data rows as of F63/F64 — up from the 51 Ruling 51
# itself measured at `01ba0bd`, because the register has grown **and** because the count
# Ruling 51 used came from the parser this same file's header-detection fix corrects: the
# 51-row figure and this 61-row one are not directly comparable measurements of the same
# thing. `len(row.raw)` — the full markdown table row, matching how Ruling 51 itself
# measured F27 and F-W9-3): the corpus is sharply bimodal, not smoothly distributed — 22
# rows sit at or under 472 characters, then every one of the remaining 39 sits at or over
# 1017, with **nothing at all between 473 and 1016**. 1000 falls inside that empty gap, so
# the constant is not tuned to hit a target count; any value in the gap partitions the
# corpus identically, which is also why the constant is robust to the corpus growing — a
# new row lands either clearly short or clearly long, never near the boundary. A migrated
# row's essay moves to its own file, which is exactly what drops its raw row length back
# under the threshold — so a migrated row leaves the residue count by construction, with no
# second "is this migrated" field to define, maintain, or let drift from the row itself.
#
# **39 of 61 rows over threshold today is a long migration, and that is the accepted
# design, not a defect** (Ruling 51 §2): the alternative it rejected was a bulk sweep (an
# unreviewable diff) or a two-row token migration that would discharge under a tenth of the
# problem while reading as having discharged it. This aggregate line is what keeps a long,
# opportunistic migration honest rather than lapsed.
ROW_LENGTH_THRESHOLD = 1000


def residue(rows: list[Row]) -> tuple[int, int]:
    """(rows over `ROW_LENGTH_THRESHOLD`, total rows) — the two figures Ruling 51 requires
    the aggregate residue line to report, alongside the threshold itself. Never per-row.
    """
    over = sum(1 for r in rows if len(r.raw) > ROW_LENGTH_THRESHOLD)
    return over, len(rows)


def residue_line(path: pathlib.Path, rows: list[Row]) -> str:
    over, total = residue(rows)
    return (
        f"{path.name}: residue — {over} of {total} row(s) exceed the "
        f"{ROW_LENGTH_THRESHOLD}-character findings-file migration threshold (Ruling 51). "
        "Not a violation — opportunistic-on-amendment only; this line is what makes that "
        "claim falsifiable rather than assumed."
    )


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
        rows, _problems = parse_register(target)
        print(residue_line(target, rows))
    if all_failures:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
