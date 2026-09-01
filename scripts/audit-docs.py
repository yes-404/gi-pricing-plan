#!/usr/bin/env python3
"""Consistency audit for the docs/ specification suite and the docs/notes/ working notes.

Checks (all non-destructive, exit 1 on any failure):
  1. No broken relative markdown links.
  2. Every referenced FR-/NFR- id is defined exactly once in a spec, except an id a
     plan lists after "Next free:" — an allocation note, not a citation.
  3. No gaps in requirement numbering within a module.
  4. Every spec open question is mirrored in open-questions.md, and vice versa.
  5. Every referenced ADR file exists.
  6. Every spec has the ten sections required by CLAUDE.md §5.
  7. Every JSON Schema parses and has no duplicate keys.
  8. Every JSON Schema $ref resolves, including cross-file pointers into $defs.
  9. Cross-spec section references ("01 §4.5") point at sections that exist.
 10. No error code is claimed as owned by more than one module.
 11. Module dependency direction respects DEP-1 (no consuming from the right).
 12. Money fields (*_minor) are never written as fractional numbers.
 13. Terms are not redefined in a module glossary after 00-overview defines them.
 14. Every module is exercised by at least one workflow, above a coverage floor.
 15. Every open-question row has an owner and a status from a known set.
 16. Every working note carries the header block docs/notes/README.md requires.
 17. Note numbering is well-formed and unique, and matches each file's own heading.
 18. The notes index and the directory agree, in both directions.
 19. Every reference a note makes resolves — links, FR-/NFR- ids, OQ- ids, ADRs, NT- ids.
 20. No note defines a requirement id; only docs/specs/ may do that.
 21. Every endpoint and pricing-core function a workflow journey cites is declared
     in the owning module's §5.1 or §5.2 (FR-OVR-17, OQ-OVR-6).
 22. Every markdown table row has its own header's cell count — catching a literal
     `|` inside a cell, which shifts every column after it while still rendering.
 23. Every spec §10 open-question mirror row carries a status token matching the
     findings register's status for that question, not just a bare, unstatused mirror.
 24. Every route `00` §5.6 declares as canonical for a module appears in that module's
     own §5.3 view table (FR-OVR-22); §5.6 is canonical, so a mismatch is a §5.3 error.
 25. Every `(F<n>)` / `(F-W<n>-<n>)` finding id cited in docs/research/, docs/plans/ or
     docs/notes/ resolves against docs/audit/register.md, an archived phase register, or
     a docs/audit/work/*/README.md (or closure-records.md) work-item closure record.
 26. Every `source` citation in docs/process/delivery-process.core.json resolves to a
     real section, or numbered step, of docs/process/delivery-process.md (NT-0014 §3).
 28. Every filed plan (the `writing-plans` file kind, dated on or after 2026-08-31) states
     an explicit "Acceptance Standard" heading with content under it (NT-0014 §2 C1,
     Ruling 46). Plans dated before the cutoff, and the `-ledger`/`-final-review`/
     `-verified`/`-handover` file kinds, are out of scope by design — never retro-red-gated.
 29. Every Decision cell in docs/audit/register.md opens with the register's own disposition
     vocabulary, a CLAUDE.md §13 verdict, or the negated fix-before-close shape; every
     resolution annotation names a date and a PR/commit/doc reference; every unowned row
     says more than the bare word (Ruling 50, `scripts/register-lint.py`). Also prints, as a
     note rather than a failure, the count of rows not yet migrated to
     docs/audit/findings/<F-id>.md against the migration threshold (Ruling 51, NT-0015 P4).
 30. The vacated .claude/notes/ tombstone holds exactly the README plus a frozen,
     closed set of 18 per-file redirect stubs, each byte-identical to a rendered
     template — a stray file or an edited stub body both fail (Ruling 61).

Usage: python3 scripts/audit-docs.py
"""
from __future__ import annotations

import collections
import hashlib
import importlib.util
import json
import pathlib
import re
import sys
import types
from datetime import date
from typing import Final

REPO = pathlib.Path(__file__).resolve().parent.parent
ROOT = REPO / "docs"
NOTES = REPO / "docs" / "notes"

# Ruling 61: the vacated .claude/notes/ tombstone -- a frozen, closed registry, not
# derived from the README's own mapping table (same reasoning as Ruling 59's census
# carve-out: a stray edit to the source of truth must not also defeat the check).
OLD_NOTES = REPO / ".claude" / "notes"
OLD_NOTES_TOMBSTONE_DATE: Final = "2026-09-01"
OLD_NOTES_STUB_NAMES: Final[tuple[str, ...]] = (
    "0001-phase-boundary-plan-review.md",
    "0002-demo-entrance-and-guide.md",
    "0003-duplicated-status-goes-stale.md",
    "0004-a-reference-that-resolves-only-for-the-writer.md",
    "0005-deferred-items-with-no-durable-custody.md",
    "0006-two-rules-for-reading-an-artifact.md",
    "0007-context-bound-measures-cap-not-discipline.md",
    "0008-project-closure-audit-structure.md",
    "0009-slim-the-roadmap.md",
    "0010-layered-slice-based-workflow.md",
    "0011-per-agent-model-and-skill-settings.md",
    "0012-a-credential-is-borrowed-not-stored.md",
    "0013-the-lead-is-the-highest-error-node.md",
    "0014-machine-readable-process-core.md",
    "0015-the-register-is-a-ledger-evidence-is-a-file.md",
    "0016-file-taxonomy-reference-coding-and-custody-investigation.md",
    "0017-a-public-repository-needs-a-public-face.md",
    "0018-a-turn-that-ends-strands-what-it-started.md",
)
_ABS_PREFIX = "https://contracts.gi-pricing.dev/"
# docs/plans/ only: ids listed after this marker are being allocated, not cited. See check 2.
UNALLOCATED = re.compile(r"next free\s*:", re.IGNORECASE)
REQUIRED_SECTIONS = [
    "Purpose & scope", "Concepts & glossary", "Functional requirements",
    "Data contracts", "Interfaces", "Workflows", "Cross-module dependencies",
    "Tech dependencies", "Non-functional requirements", "Open questions",
]

failures: list[str] = []
notes: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)


# scripts/register-lint.py — check 29's implementation. A hyphenated filename cannot be
# `import`ed; loaded by path, as `bench-trace-size.py` already does for `bench-rating.py`.
def _load_register_lint() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(
        "_register_lint", REPO / "scripts" / "register-lint.py"
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_register_grammar() -> None:
    """Check 29: docs/audit/register.md's Decision-cell grammar (Ruling 50), plus the P4
    findings-file migration residue line (Ruling 51) — a note, never a failure, so the
    "opportunistic migration" claim stays falsifiable everywhere the docs gate runs, not
    only when `register-lint.py` is invoked directly.
    """
    register = ROOT / "audit" / "register.md"
    if not register.exists():
        notes.append("no docs/audit/register.md — check 29 skipped")
        return
    register_lint = _load_register_lint()
    violations = register_lint.lint_register(register)
    for v in violations:
        fail(f"check 29: {v}")
    notes.append(f"check 29: register grammar — {len(violations)} violation(s)")
    rows, _problems = register_lint.parse_register(register)
    notes.append(f"check 29: {register_lint.residue_line(register, rows)}")




#: `| \`GET\` | \`/api/v1/datasets\` | … |` — a §5.1 REST API row. The method cell may hold
#: several (\`GET\`/\`PUT\`); the path cell may hold several paths. Deliberately the same
#: shape `scope-audit.py` uses, because the two scripts read the same tables and a second
#: parser would eventually disagree with the first about what the spec declares.
_ENDPOINT_ROW = re.compile(r"^\|\s*`?([A-Z]+(?:`?/`?[A-Z]+)*)`?\s*\|([^|]+)\|")


def _path_segments(path: str) -> tuple[str, ...]:
    """A path as comparable segments, with `{placeholders}` collapsed.

    The `/api/v1` prefix is dropped: the specs' tables carry it and the journeys do not, and
    the prefix is a deployment fact rather than part of which endpoint is meant. A query
    string documents filters, not a different route (`scope-audit.py` settled that).
    """
    clean = path.split("?")[0].removeprefix("/api/v1")
    return tuple(
        "{}" if segment.startswith("{") and segment.endswith("}") else segment
        for segment in clean.strip("/").split("/")
    )


def _placeholder_match(
    key: tuple[str, tuple[str, ...]], declared: dict[tuple[str, tuple[str, ...]], str]
) -> str | None:
    """A declared `{}` segment matches a literal one in a citation.

    Needed because a journey is concrete where the spec is general — wf-04 deploys to `prod`,
    and `03` §5.1 declares `/environments/{env}/deployments`. Refusing that would report four
    working, declared endpoints as missing, and a check that cries wolf is one everybody
    learns to skip.

    Exact matches are tried **first** by the caller, so this only runs when nothing matched
    literally. It is the one place the check is weaker than a strict comparison: a citation of
    `/models/nonsense` would match a declared `/models/{}`. The caller counts every use and
    prints the count, so the looseness is visible rather than assumed away.
    """
    method, segments = key
    for (dm, ds), owner in declared.items():
        if dm != method or len(ds) != len(segments):
            continue
        if all(d == s or d == "{}" for d, s in zip(ds, segments, strict=True)):
            return owner
    return None

def check_open_question_columns() -> None:
    """15. Every OQ row has an owner and a status drawn from a known set.

    Added after an edit wrote "decided" into the *owner* column and left the status as
    "open": the register then disagreed with the spec about whether a question was settled,
    and all fourteen existing checks passed. A malformed row here is not a typo — this file
    is the project's record of what has been decided.
    """
    allowed = {"open", "decided", "deferred", "superseded"}
    path = ROOT / "open-questions.md"
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = re.match(r"\| (?:~~)?\*\*(OQ-[A-Z]+-\d+)\*\*", line)
        if not match:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            fail(f"open-questions.md:{number}: {match.group(1)} has too few columns")
            continue
        owner = cells[-2].replace("*", "").strip().lower()
        status = cells[-1].replace("*", "").replace("~", "").strip().lower()
        first = status.split()[0] if status else ""
        if first not in allowed:
            fail(
                f"open-questions.md:{number}: {match.group(1)} status {cells[-1]!r} is not "
                f"one of {sorted(allowed)}"
            )
        if not owner or owner in allowed:
            fail(
                f"open-questions.md:{number}: {match.group(1)} owner {cells[-2]!r} looks "
                "like a status — the columns may be shifted"
            )


def check_open_question_mirror_status(specs: list[pathlib.Path]) -> None:
    """23. Every spec §10 mirror row carries a status token matching the register's.

    Check 4 proves every question is mirrored in both directions, but nothing looks at
    what the mirror row *says*. A bare row — the question, no status, no consequence —
    is audit-clean by construction, even when the register has long since decided the
    question; OQ-OVR-7's two bodies had diverged so far they named different things
    while every check passed. The register is the source of truth (check 15 constrains
    its status vocabulary), so each mirror row must state its status in the register's
    own words: a decided question's row must carry "decided" (or a mirror-side
    synonym), an open one "open", a deferred one "deferred".

    Scoped to each spec's §10: a requirement row citing an OQ id elsewhere in the spec
    is a reference, not a mirror. Anchored to the row: the status token must follow the
    id on the same row, so a neighbouring row's status never satisfies it.
    """
    register: dict[str, str] = {}
    path = ROOT / "open-questions.md"
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\| (?:~~)?\*\*(OQ-[A-Z]+-\d+)\*\*", line)
        if not match:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        status = cells[-1].replace("*", "").replace("~", "").strip().lower()
        register[match.group(1)] = status.split()[0] if status else ""

    # The register's own vocabulary is check 15's {open, decided, deferred, superseded};
    # mirrors have historically written a decided question as "resolved" or "determined".
    groups = {
        "open": {"open"},
        "decided": {"decided", "resolved", "determined"},
        "deferred": {"deferred"},
        "superseded": {"superseded"},
    }

    checked = ok = 0
    for f in specs:
        lines = f.read_text(encoding="utf-8").splitlines()
        start = next(
            (i for i, ln in enumerate(lines) if re.match(r"^## 10\.", ln)), None
        )
        if start is None:
            continue
        for i in range(start + 1, len(lines)):
            line = lines[i]
            if line.startswith("## "):
                break
            m = re.search(r"\*\*(OQ-[A-Z]+-\d+)\*\*", line)
            if not m:
                continue
            oq = m.group(1)
            reg_status = register.get(oq)
            if not reg_status:
                continue  # the both-ways mirror itself is check 4's
            checked += 1
            after = line[m.end():]
            if not any(
                re.search(rf"\b{re.escape(word)}\b", after, re.IGNORECASE)
                for word in groups.get(reg_status, {reg_status})
            ):
                fail(
                    f"{f.name}:{i + 1}: {oq} mirror row carries no status token matching "
                    f"the register's {reg_status!r} status"
                )
            else:
                ok += 1
    # The verdict belongs in the summary line, not just the failure list: a note reading
    # "all carry" above a FAILED block is the shape this audit exists to catch.
    notes.append(f"{ok} of {checked} §10 mirror rows carry their register status")


def check_notes_tombstone() -> None:
    """30. The vacated `.claude/notes/` tombstone: exactly the README plus the frozen,
    closed set of per-file redirect stubs (Ruling 61), each byte-identical to a rendered
    template.

    Ruling 57 (`docs/plans/2026-09-01-nt-0016-q4-q5-q6-q7-notes-rulings.md`) chose a single
    README tombstone at the vacated path. NT-0016 Slice 4's own execution found that a
    directory-level README does not make an *individual* old-path citation resolve: 13
    frozen plans under `docs/plans/` cite notes by their old path
    (`../../.claude/notes/000N-....md`), C4 forbids editing a frozen plan to fix its
    citation, and check 1 (broken links) tests on-disk existence per link target, not per
    directory. The fix was 18 one-line redirect stubs, one per moved note -- which fixed
    check 1, but sat at a location nothing in this script reads any more (`NOTES` points at
    `docs/notes/`, `docs.yml`'s path filter no longer names the old path). Ruling 61 kept
    the stubs and required this check: without it, a stray file or an edited stub body at
    the old path would be invisible to every check in this script, recreating -- in a
    different shape -- exactly the unwatched-drift risk Ruling 57's own tombstone design
    was chosen to avoid.

    **A frozen, closed registry, not a re-parse of the README's own mapping table** -- the
    same design choice Ruling 59 made for the file-census provenance carve-out, for the same
    reason: deriving the expected set from a file a stray edit could also touch would let
    one edit defeat both the content it changes and the check meant to catch the change.
    `OLD_NOTES_STUB_NAMES` is that registry.

    Three things are checked, in order:

    1. `OLD_NOTES` is unconditionally expected to exist as a directory -- the same posture
       `check_notes` already takes for `NOTES` itself.
    2. **Exact membership.** The `*.md` basenames actually present must equal
       `{"README.md", *OLD_NOTES_STUB_NAMES}` -- not a superset or subset check. A name
       present on disk and absent from the registry is a stray file; a registered name
       absent from disk is a deleted stub. Either way, a mismatched set is reported by name
       rather than only by count, so the failure names exactly what changed.
    3. **Exact content, per stub.** Each registered stub's bytes must equal a template
       rendered from its own name, deterministically -- not a regex or a prefix match.
       Ruling 59's own record already found a byte-exact comparison stronger and no more
       expensive than a looser pattern match for a template this short, and the same
       reasoning applies here: a body edited in any way -- a typo fix, an added sentence,
       real content pasted in -- fails.

    `README.md` itself is not re-validated here: Ruling 57 already specifies its content,
    and this check's job is the 18 files that specification does not cover.
    """
    if not OLD_NOTES.is_dir():
        fail(f"{OLD_NOTES.relative_to(REPO).as_posix()} does not exist — check 30 cannot run")
        return

    expected_names = {"README.md", *OLD_NOTES_STUB_NAMES}
    actual_names = {p.name for p in OLD_NOTES.glob("*.md")}

    stray = sorted(actual_names - expected_names)
    for name in stray:
        fail(
            f"{OLD_NOTES.relative_to(REPO).as_posix()}/{name} is not a registered stub "
            "(Ruling 61) — a stray file at the vacated notes path is invisible to every "
            "other check in this script"
        )

    missing = sorted(expected_names - actual_names)
    for name in missing:
        fail(
            f"{OLD_NOTES.relative_to(REPO).as_posix()}/{name} is registered (Ruling 61) "
            "but missing from disk"
        )

    for name in OLD_NOTES_STUB_NAMES:
        stub = OLD_NOTES / name
        if not stub.is_file():
            continue  # already reported above as missing
        expected = (
            "# Moved\n\n"
            f"This note moved to [`docs/notes/{name}`](../../docs/notes/{name}) on "
            f"{OLD_NOTES_TOMBSTONE_DATE} (NT-0016 Slice 4). See [this directory's "
            "README](README.md) for the full mapping and why this stub exists rather "
            "than a symlink (Ruling 57).\n"
        )
        actual = stub.read_text(encoding="utf-8")
        if actual != expected:
            fail(
                f"{OLD_NOTES.relative_to(REPO).as_posix()}/{name} does not match its "
                "rendered template (Ruling 61) — a stub body was edited, and nothing "
                "downstream of the old path would otherwise notice"
            )


def check_notes(defined: set[str], questions: set[str], adrs: set[str]) -> None:
    """16-20. The working notes in docs/notes/, against that directory's README.

    The notes are not the specification, so most of their audit standard is judgement — is
    this status still true of the repository, is this deliverable still right for the phase
    the project is now in. A script cannot answer either. What it *can* answer is every
    mechanical part, and those are precisely the ones that rot without anyone noticing: a
    reference to a file that has been renamed, a number reused after a deletion, an index
    that no longer lists what the directory holds.

    Two limits are worth stating rather than implying. **Number reuse across a deletion is
    not detectable here** — a snapshot cannot see the retired number, so that check stays
    manual and stays in the README. And gaps in the sequence are *legal*: a deleted note
    retires its number, so contiguity is deliberately not asserted. A missing `NOTES` root is
    an **error**, not a legitimate absence: unlike an artifact the repository may not have
    built yet, this directory is unconditionally present, so its disappearance can only mean
    a move or a deletion that forgot to update this check.
    """
    if not NOTES.is_dir():
        fail(
            f"{NOTES.relative_to(REPO).as_posix()} does not exist — checks 16-20 cannot run"
        )
        return

    def rel(path: pathlib.Path) -> str:
        return path.relative_to(REPO).as_posix()

    def head_word(cell: str) -> str:
        """First word of a status cell, stripped of markdown emphasis."""
        cleaned = cell.replace("`", "").replace("*", "").replace("~", "").strip().lower()
        return cleaned.split()[0].rstrip(",.;:") if cleaned else ""

    allowed = {"open", "accepted", "landed", "superseded", "dropped"}
    required = ("Raised", "Status", "Deliverable", "Owner", "Lands in")
    files = sorted(p for p in NOTES.glob("*.md") if p.name != "README.md")
    seen: dict[str, pathlib.Path] = {}
    status_of: dict[str, str] = {}
    cited: dict[pathlib.Path, set[str]] = {}

    for f in files:
        text = f.read_text(encoding="utf-8")
        fields = dict(re.findall(r"^\| \*\*(.+?)\*\* \| (.+?) \|\s*$", text, re.M))

        # 16. the header block README.md requires
        for name in required:
            if name not in fields:
                fail(f"{rel(f)}: header block is missing the **{name}** field")
        if not any(k.startswith(("Sequencing", "Trigger")) for k in fields):
            fail(f"{rel(f)}: header block needs a **Sequencing** or **Trigger** field")
        status = head_word(fields.get("Status", ""))
        if status not in allowed:
            fail(
                f"{rel(f)}: status {fields.get('Status', '(absent)')!r} is not one of "
                f"{sorted(allowed)}"
            )

        # 17. numbering, and the heading that must agree with it
        match = re.match(r"^(\d{4})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$", f.name)
        if not match:
            fail(f"{rel(f)}: filename is not of the form NNNN-kebab-title.md")
        else:
            number = match.group(1)
            heading = re.search(r"^# NT-(\d{4})\b", text, re.M)
            if not heading:
                fail(f"{rel(f)}: first heading must read '# NT-{number} — <title>'")
            elif heading.group(1) != number:
                fail(
                    f"{rel(f)}: heading says NT-{heading.group(1)} but the filename "
                    f"says {number} — a note has one identity"
                )
            if number in seen:
                fail(
                    f"note number NT-{number} is used by both {rel(seen[number])} and "
                    f"{rel(f)} — numbers are unique and never reused"
                )
            seen[number] = f
            status_of[number] = status

        # 19. every reference resolves
        for m in re.finditer(r"\[[^\]]*\]\(([^)#\s]+)(#[^)]*)?\)", text):
            target = m.group(1)
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            if not (f.parent / target).resolve().exists():
                fail(f"{rel(f)}: broken link: {target}")
        for rid in sorted(set(re.findall(r"\b((?:FR|NFR)-[A-Z]+-\d+)\b", text)) - defined):
            fail(f"{rel(f)}: references {rid}, which no spec defines")
        for oq in sorted(set(re.findall(r"\b(OQ-[A-Z]+-\d+)\b", text)) - questions):
            fail(f"{rel(f)}: references {oq}, which open-questions.md does not list")
        for ref in sorted(set(re.findall(r"ADR-(\d{4})", text)) - adrs):
            fail(f"{rel(f)}: references ADR-{ref}, for which no file exists")
        # NT- ids are resolved after the loop: a note may cite one numbered above it.
        cited[f] = set(re.findall(r"\bNT-(\d{4})\b", text)) - {f.name[:4]}

        # 20. a note may propose a requirement; it may never define one
        for rid in sorted(set(re.findall(r"\*\*((?:FR|NFR)-[A-Z]+-\d+)\*\*", text))):
            fail(
                f"{rel(f)}: defines {rid} in the bold form reserved for docs/specs/ — "
                "a note may propose a requirement, never carry one"
            )

    # 18. the index and the directory, in both directions
    readme = NOTES / "README.md"
    if not readme.is_file():
        fail("docs/notes/README.md is missing — the index is part of the standard")
        return
    indexed: dict[str, tuple[str, str]] = {}
    for line in readme.read_text(encoding="utf-8").splitlines():
        row = re.match(r"^\| \[NT-(\d{4})\]\(([^)]+)\)", line)
        if not row:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        indexed[row.group(1)] = (row.group(2), cells[3] if len(cells) > 3 else "")
    for number, path in sorted(seen.items()):
        if number not in indexed:
            fail(f"{rel(path)} is not listed in the docs/notes/README.md index")
        elif indexed[number][0] != path.name:
            fail(
                f"index row NT-{number} links to {indexed[number][0]}, but the file is "
                f"{path.name}"
            )
        elif head_word(indexed[number][1]) != status_of[number]:
            fail(
                f"note NT-{number}: index says status "
                f"{head_word(indexed[number][1])!r}, the file says {status_of[number]!r}"
            )
    for number in sorted(set(indexed) - set(seen)):
        fail(f"index lists note NT-{number}, but no such file exists in docs/notes/")

    # 19, second pass: a note citing another note — a `superseded` row must name a real one,
    # and a retired number must not be quietly resurrected by a reference to it.
    for f, refs in sorted(cited.items()):
        for ref in sorted(refs - set(seen)):
            fail(f"{rel(f)}: references NT-{ref}, for which no note exists")
    notes.append(f"{len(files)} working notes, indexed and numbered")


def check_table_rows(md: list[pathlib.Path]) -> None:
    r"""Check 22: every table row has as many cells as its own header.

    The defect this catches is a literal `|` inside a table cell. GFM decides cell
    boundaries **before** it parses anything inline, so a pipe inside a code span still
    splits the row — `` `rows | parquet` `` silently becomes two cells, and every column
    after it shifts right. The row still renders, which is why nothing noticed: the table
    looks intact and the last cell's content has quietly moved into a column that means
    something else. Escaping (`` `rows \| parquet` ``) is the only fix, and it works inside
    a code span even though a backslash escape normally does not.

    Found 2026-08-18 in two rows written the same day — `03` FR-RATE-62 and OQ-RATE-3's
    register entry — where the Owner column had become part of the recommendation.

    Rows are compared against their **own table's** header rather than a per-file majority:
    a document legitimately holds tables of different widths, and this suite's files nearly
    all do.
    """
    for f in md:
        fenced = False
        header_cells: int | None = None
        for lineno, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.lstrip()
            if stripped.startswith("```"):
                fenced = not fenced
                continue
            if fenced or not stripped.startswith("|"):
                # A blank line (or any prose) ends the table, so the next one sets its own
                # width. Without this the second table in a file is measured against the
                # first, which is the false positive that makes a check like this ignorable.
                header_cells = None
                continue
            cells = len(re.findall(r"(?<!\\)\|", line)) - 1
            if header_cells is None:
                header_cells = cells
                continue
            if cells != header_cells:
                where = f"{f.relative_to(REPO)}:{lineno}"
                offenders = re.findall(r"`[^`]*(?<!\\)\|[^`]*`", line)
                detail = f" — unescaped pipe in {offenders[0]}" if offenders else ""
                fail(
                    f"table row has {cells} cells, its header has {header_cells} "
                    f"({where}){detail}"
                )


#: `F6`, `F26`, or the workstream-scoped `F-W9-1` / `F-W10-1-1` a phase-boundary carry-forward
#: uses — the findings register's own id shape, confirmed against every row in
#: `docs/audit/register.md` and `docs/audit/phases/*/register.md`.
_FINDING_ID = r"F(?:-W\d+-\d+(?:-\d+)?|\d+)"
#: The register's own citation convention: a finding id in parentheses, immediately after the
#: text it concerns — `` `Ruling 16's acceptance-test premise (F32)` ``. See
#: `check_finding_citations`'s docstring for why a bare `F1` is deliberately not matched.
_FINDING_CITED = re.compile(r"\((" + _FINDING_ID + r")\)")
#: A file defining its own local, private findings — a heading (`## F1 — …`), a ledger
#: table's own first cell (`| F1 | … |`, the shape both `track-a-findings.md` and every
#: archived phase register use), or a bold paragraph lead-in (`**F-W11-1-2 — … .**`, the
#: shape `docs/plans/2026-08-29-w11-1-evaluator-core.md` uses for its own four findings).
_FINDING_HEADING = re.compile(r"^#{1,6}\s+(" + _FINDING_ID + r")\b", re.M)
_FINDING_TABLE_CELL = re.compile(r"^\|\s*(" + _FINDING_ID + r")\s*\|", re.M)
_FINDING_BOLD_LEAD = re.compile(r"^\*\*(" + _FINDING_ID + r")\b", re.M)


def check_finding_citations() -> None:
    r"""25. Every finding id cited outside the register resolves to a row there.

    `docs/audit/register.md` is the single register of open findings (`CLAUDE.md` §13), and
    until now nothing checked it from the *citing* side: a plan, a research spike or a working
    note can write `(F42)` for a withdrawn finding, or `(F45)` for one a tombstone note had
    just promised but no row yet existed for, and nothing complained. Both happened for real
    on 2026-08-29, caught only because someone happened to remember the register's actual
    contents rather than by anything mechanical.

    **Scope is deliberately narrow: `docs/research/`, `docs/plans/` and `docs/notes/` only**
    — where a citation is *made*. Not `docs/audit/` itself, where findings are *filed* and a
    retired id or a not-yet-filed one is legitimately named in the prose explaining exactly
    that (the F42 tombstone note names both F42 and F45 in plain, unparenthesised text for
    this reason). Not `docs/roadmap.md` or `docs/phase-0-status.md` either, though both carry
    `(F..)` tokens: building this check found `phase-0-status.md`'s `(F13)` citing
    `docs/research/track-a-findings.md`'s own local F13 (`FR-MODEL-72`) — a real collision
    with the register's *unrelated* F13 (`FR-OVR-22`) that a wider scan would have silently
    resolved against the wrong row instead of catching. Narrowing to where the incident this
    check answers actually happened is what keeps that kind of false confidence out.

    **All three scan roots are unconditionally present, so a missing one is an error, not a
    legitimate absence.** Unlike an artifact the repository may not have built yet, `research/`,
    `plans/` and `docs/notes/` are the same three named just above as this check's
    deliberate, symmetric scope — none of them is optional relative to the other two, so a
    `git mv` of any one would silently narrow this check's coverage were its disappearance
    only skipped rather than reported.

    **Only the register's own citation form is matched**: an id in parentheses immediately
    after the text it concerns, `(F32)` or `(F-W9-1)` — exactly how every register row names
    itself, and how every genuine cross-document citation found while writing this check was
    written (`docs/plans/2026-08-29-w11-3-batch-scoring.md` and its W11 siblings). A bare
    `F1` with no parentheses is deliberately never matched: dozens of unrelated documents
    number their *own* local findings from one — every W5 and W6b task plan's own "Findings"
    section, `track-a-findings.md`'s spike log, the phase 1b predecision plan before it became
    that phase's register — and a bare-token scan over `docs/plans/` and `docs/research/`
    flagged several hundred of those as dangling register references against the corpus this
    check was actually written against. Parenthesising is the one marker that survived contact
    with the real corpus; the cost is a real citation written some other way (a comma-separated
    list, a bare id) is not checked, which is preferred over a check that cries wolf.

    **A file citing its own locally-defined finding is not citing the register.** A plan that
    opens `### F1 — …` (a heading), or `**F-W11-1-2 — … .**` (a bold paragraph lead-in, the
    form `docs/plans/2026-08-29-w11-1-evaluator-core.md` uses for its own four findings), and
    later writes `(F1)` or `(F-W11-1-2)` again further down, refers to itself, not to
    `docs/audit/register.md`. `_FINDING_HEADING`, `_FINDING_TABLE_CELL` and
    `_FINDING_BOLD_LEAD` collect a file's own local ids (all three defining forms seen in the
    real corpus), same-file only: a citation resolved by a *different* file's local heading
    (the `phase-0-status.md` collision above) is exactly the false match this check must not
    make, which is a second, independent reason that file sits outside this check's scope.

    **A finding resolves against the live register, an archived phase register, or a closure
    record — never only the first.** `docs/audit/register.md`'s own header states the
    contract: one row per *open* finding, removed when a close resolves it. A finding can
    therefore be real, correctly resolved, and correctly cited, while having never had a row
    in the live register at all — the ordinary case for one closed during a slice's own audit
    rather than carried forward. `F-W9-3-2` is exactly this shape: resolved the same day it
    was raised (`docs/audit/work/W9-3/README.md`'s Findings table), cited from the spec
    sentence it corrected (`03-rating-engine.md:671`), never filed to `register.md` because
    filing a *closed* finding there would violate the header's own contract. Ruling, 2026-08-30
    (relayed from the lead, who cannot reach this script directly): treating that citation as
    dangling — the check's first version did — is a worse defect than the gap the check exists
    to catch, since it fires on correct behaviour. Resolution therefore checks three sources in
    order: `register.md` (open findings, parenthesised `(F<n>)` form), every
    `docs/audit/phases/*/register.md` (archived-phase snapshots, bare-id table-cell form), and
    every `docs/audit/work/*/README.md` plus `docs/audit/closure-records.md` (ordinary work-item
    closure records, the same bare-id table-cell form — confirmed against `W9-3`'s own Findings
    table before relying on it, not assumed from the name).

    **The reverse direction — a register row citing a document that does not exist — is
    deliberately not built here.** A genuine `[text](path)` link inside `docs/audit/
    register.md` is already covered by check 1, which scans all of `docs/` including
    `docs/audit/`. Past that, the register's backtick spans are not reliably file paths: one
    row alone mixes a real path, a code symbol, a `file.py:NNN` citation, a shell command and
    an error-code name with no syntactic marker telling them apart — the same false-positive
    risk the citation side above was narrowed to avoid, not yet worth the same risk twice in
    one check.
    """
    registered: set[str] = set()
    register_file = ROOT / "audit" / "register.md"
    if register_file.is_file():
        registered |= set(_FINDING_CITED.findall(register_file.read_text(encoding="utf-8")))
    for phase_register in sorted((ROOT / "audit" / "phases").glob("*/register.md")):
        registered |= set(
            _FINDING_TABLE_CELL.findall(phase_register.read_text(encoding="utf-8"))
        )
    # Work-item closure records: a finding closed during its own slice's audit never gets a
    # register.md row at all (the register holds only open findings) but is no less real, no
    # less resolved, and no less a legitimate thing to cite -- confirmed against W9-3's own
    # Findings table, whose id is the bare first cell, the same shape a phase register uses.
    closure_sources = sorted((ROOT / "audit" / "work").glob("*/README.md"))
    closure_records = ROOT / "audit" / "closure-records.md"
    if closure_records.is_file():
        closure_sources.append(closure_records)
    for source in closure_sources:
        registered |= set(_FINDING_TABLE_CELL.findall(source.read_text(encoding="utf-8")))

    scan_dirs = [ROOT / "research", ROOT / "plans", NOTES]
    scanned_files: set[pathlib.Path] = set()
    for d in scan_dirs:
        if not d.is_dir():
            fail(f"{d.relative_to(REPO).as_posix()} does not exist — check 25 cannot scan it")
            continue
        scanned_files |= set(d.rglob("*.md"))
    scanned = sorted(scanned_files)
    for f in scanned:
        text = f.read_text(encoding="utf-8")
        cited = set(_FINDING_CITED.findall(text))
        local = (
            set(_FINDING_HEADING.findall(text))
            | set(_FINDING_TABLE_CELL.findall(text))
            | set(_FINDING_BOLD_LEAD.findall(text))
        )
        for fid in sorted(cited - registered - local):
            fail(
                f"{f.relative_to(REPO)}: cites finding {fid}, which resolves nowhere -- "
                "not docs/audit/register.md, not an archived phase register, not a "
                "docs/audit/work/*/README.md or closure-records.md closure record, and not "
                "defined locally in this file"
            )


PROCESS_SPEC = REPO / "docs" / "process" / "delivery-process.md"
PROCESS_CORE = REPO / "docs" / "process" / "delivery-process.core.json"

#: `§7`, or `§5.4` for step 4 of §5's numbered list. `§N.M` is a *step*, not a `###`
#: subsection — `delivery-process.md` has no `###` headings at all, so a reader who assumed
#: subsections would report every step citation as dangling.
_CITATION = re.compile(r"§(\d+)(?:\.(\d+))?")


def check_process_core_drift() -> None:
    """26. Every `source` citation in the process core extract resolves in the process spec.

    `docs/process/delivery-process.core.json` is the machine-readable extract of
    `delivery-process.md` (NT-0014). **The markdown is authoritative and the extract is
    derived**, so an extract citing a section that does not exist means the extract is
    wrong — never the spec. The check is one-directional for that reason.

    This is the cheap half of a drift check, and it is the half that catches the failure
    which motivated the whole proposal: at `6f77abb` the process spec's own back-reference
    named `CLAUDE.md` §12 for a pointer that lives in §15, and no gate in the repository
    could see it. A citation that *resolves* is not proof the cited text still says what the
    citer thinks (`NT-0006`); a citation that does **not** resolve is proof of drift, with
    no judgement required. Only the second is mechanised here.

    Numbered 26, not 25: 25 is claimed by in-flight work, and a check number is permanent
    under `CLAUDE.md` §5 for the same reason a requirement id is.
    """
    if not PROCESS_SPEC.is_file():
        notes.append("no docs/process/delivery-process.md — check 26 skipped")
        return

    spec_text = PROCESS_SPEC.read_text(encoding="utf-8")

    if not PROCESS_CORE.is_file():
        # Not a silent skip. §10 lists the extract as a required artifact, so its absence
        # while that line stands is drift in the other direction — and a check that quietly
        # passes when its subject is deleted is a check anyone can disarm by deleting it.
        if "delivery-process.core.json" in spec_text:
            fail(
                "docs/process/delivery-process.core.json is missing, but "
                "delivery-process.md still lists it as a required artifact (§10) — "
                "restore the extract, or remove the §10 bullet that requires it"
            )
        else:
            notes.append("no process core extract, and §10 does not require one — check 26 skipped")
        return

    raw = PROCESS_CORE.read_text(encoding="utf-8")
    try:
        core = json.loads(raw)
    except json.JSONDecodeError as exc:
        fail(f"docs/process/delivery-process.core.json is not valid JSON: {exc}")
        return

    # The authority rule (NT-0014 §3) enforced on the artifact that claims it, rather than
    # only stated in the prose beside it.
    meta = core.get("meta", {})
    if meta.get("authoritative") is not False:
        fail(
            "process core `meta.authoritative` must be `false` — the markdown spec is "
            f"authoritative and the extract is derived (NT-0014 §3); found "
            f"{meta.get('authoritative')!r}"
        )
    derived = meta.get("derived_from")
    if not derived or not (REPO / derived).is_file():
        fail(
            f"process core `meta.derived_from` names {derived!r}, which is not a file in "
            "this repository — the extract must say what it is derived from"
        )

    # `## 7. Escalation guards …` → section "7"; the largest `N. ` item under it → its step
    # count, which is what a `§7.N` citation is checked against.
    steps: dict[str, int] = {}
    current: str | None = None
    for line in spec_text.splitlines():
        head = re.match(r"^## (\d+)\.", line)
        if head:
            current = head.group(1)
            steps.setdefault(current, 0)
            continue
        if current is not None:
            item = re.match(r"^(\d+)\. ", line)
            if item:
                steps[current] = max(steps[current], int(item.group(1)))

    def _sources(node: object) -> collections.abc.Iterator[str]:
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "source" and isinstance(value, str):
                    yield value
                else:
                    yield from _sources(value)
        elif isinstance(node, list):
            for value in node:
                yield from _sources(value)

    checked = 0
    uncited = 0
    for src in _sources(core):
        found = _CITATION.findall(src)
        if not found:
            uncited += 1
            fail(
                f"process core: `source` value {src!r} cites no § section — every block "
                "must name the spec section it was extracted from (NT-0014 §3)"
            )
            continue
        for section, step in found:
            checked += 1
            if section not in steps:
                fail(
                    f"process core cites §{section} (in {src!r}), but delivery-process.md "
                    f"has no `## {section}.` heading — the extract is derived, so fix the "
                    "extract, not the spec"
                )
            elif step and int(step) > steps[section]:
                fail(
                    f"process core cites §{section}.{step} (in {src!r}), but §{section} "
                    f"has only {steps[section]} numbered steps — `§N.M` means step M of "
                    "that section's list, and the spec has no `###` subsections"
                )

    if not checked and not uncited:
        fail(
            "process core carries no `source` citations at all — every block must cite the "
            "spec section it came from, which is what makes drift detectable (NT-0014 §3)"
        )
        return

    notes.append(
        f"{checked} process-core § citations, resolved against "
        f"{len(steps)} sections of delivery-process.md"
    )


def check_process_core_digest() -> None:
    """27. The process core extract's recorded digest matches the current bytes of the spec.

    Check 26 is, by its own docstring, "the cheap half of a drift check": it resolves each
    block's `source` citation but compares nothing about *content*. That gap was not
    theoretical — at the moment this check was proposed (Ruling 45,
    `docs/plans/2026-08-30-nt-0014-q1-q3-q4-rulings.md`), `delivery-process.md` had taken two
    commits past the extract's only commit, including one that added two normative rules to
    the very section (§15) a guard block cites, and check 26 stayed green throughout.

    This is the other half. `meta.derived_from_digest` records a `sha256:` digest of the
    exact bytes of `meta.derived_from` (`delivery-process.md`) as read at the last
    reconciliation, paired with the commit that reconciliation happened at
    (`meta.verified_against_tree`, already present on the artifact — Ruling 45 makes it
    load-bearing for the first time). Comparing prose to JSON semantically is not buildable;
    comparing "the source has not moved since a human last reconciled the extract against
    it" is exactly this — three lines, and the check that actually forces the reconciliation.

    The pairing with a commit is not decoration (Ruling 45 §2): a bare digest mismatch says
    only "it changed", but the recorded commit lets the failure message name the exact range
    a session should read — `git diff <verified_against_tree>..HEAD -- delivery-process.md`
    — the difference between re-reading the diff and blindly bumping a hash.

    One-directional like check 26 and for the same reason: the markdown is authoritative
    (`meta.authoritative` is `false`), so a mismatch is always the extract falling behind,
    never the spec being wrong. Known cost, accepted per the ruling: this reds on every edit
    to the process spec, including a typo — the right price for a forced re-read.

    Numbered 27, the number Ruling 45 §3 reserved (free at `1407e09`); slice F took 28,
    leaving 27 here.
    """
    if not PROCESS_SPEC.is_file():
        notes.append("no docs/process/delivery-process.md — check 27 skipped")
        return
    if not PROCESS_CORE.is_file():
        # Check 26 already fails loudly when the extract is missing but still required by
        # §10; nothing further to say about a digest with no file to read it from.
        notes.append("no process core extract — check 27 skipped (check 26 covers this)")
        return

    raw = PROCESS_CORE.read_text(encoding="utf-8")
    try:
        core = json.loads(raw)
    except json.JSONDecodeError:
        # Already reported by check 26; do not double-report the same defect.
        return

    meta = core.get("meta", {})
    recorded_tree = meta.get("verified_against_tree")
    recorded_digest = meta.get("derived_from_digest")

    if not recorded_tree:
        fail(
            "process core `meta.verified_against_tree` is missing or empty — the digest "
            "must be paired with the commit it was taken at (Ruling 45 §2), so a future "
            "mismatch can name the exact range to read"
        )

    if not recorded_digest:
        fail(
            "process core `meta.derived_from_digest` is missing — Ruling 45 requires a "
            "`sha256:`-prefixed digest of the exact bytes of `meta.derived_from` "
            "(delivery-process.md), recorded at the commit it was last reconciled against"
        )
        return

    if not recorded_digest.startswith("sha256:"):
        fail(
            f"process core `meta.derived_from_digest` {recorded_digest!r} is not "
            "`sha256:`-prefixed — Ruling 45 specifies a sha256 digest of the exact bytes"
        )
        return

    actual_digest = "sha256:" + hashlib.sha256(PROCESS_SPEC.read_bytes()).hexdigest()
    if recorded_digest != actual_digest:
        fail(
            f"process core `meta.derived_from_digest` ({recorded_digest}) does not match "
            f"the current bytes of delivery-process.md ({actual_digest}) — the spec has "
            f"changed since the extract was last reconciled at "
            f"{recorded_tree or '<unrecorded commit>'}; read "
            f"`git diff {recorded_tree or '<unrecorded commit>'}..HEAD -- "
            "docs/process/delivery-process.md`, reconcile the extract against it, and "
            "update both `meta.derived_from_digest` and `meta.verified_against_tree`"
        )
        return

    notes.append(
        f"check 27: process core digest matches delivery-process.md "
        f"(reconciled at {recorded_tree})"
    )


#: The date C1 and the `writing-plans` acceptance-standard field land together (NT-0014 §2,
#: Ruling 46 — `docs/plans/2026-08-30-nt-0014-q1-q3-q4-rulings.md` Ruling 46). A constant, not
#: read from the clock or git history: the verdict must be a property of the plan's own
#: filename, reproducible in any clone at any revision, never of when the check happens to
#: run. **Permanent once landed, the same way a check number is (`CLAUDE.md` §5) — do not
#: move it forward to "catch up" a plan filed between this date and today.**
PLAN_ACCEPTANCE_STANDARD_CUTOFF = date(2026, 8, 31)

#: docs/plans/README.md's four file kinds: the plan itself carries no suffix; these four do,
#: and none of them declares an acceptance standard of their own (Ruling 46 §2). A filename
#: not matching one of these and not carrying a `YYYY-MM-DD-` prefix is a naming defect the
#: check refuses outright, rather than silently guessing which kind it is.
_PLAN_KIND_EXCLUDED_SUFFIXES = ("-ledger.md", "-final-review.md", "-verified.md", "-handover.md")
_PLAN_FILENAME_DATE = re.compile(r"^(\d{4}-\d{2}-\d{2})-")
_ACCEPTANCE_STANDARD_HEADING = re.compile(r"^#{1,6}\s+.*acceptance standard", re.IGNORECASE)


def check_plan_acceptance_standard() -> None:
    """28. A filed plan (the `writing-plans` file kind) states an explicit acceptance standard.

    Mechanises NT-0014's C1 and `delivery-process.md` §5 step 4 / §6 step 1: the lead's
    replan-vs-proceed check that "an acceptance standard was actually defined, not just
    implied." A bare heading is not "actually defined" either, so the check also requires
    content under it — but it cannot judge whether that content is a *good* standard; that
    stays the lead's read (`.claude/roles/lead.md`).

    **The discriminator is Ruling 46's, not a warn-then-red switch**: a plan's own filename
    date against `PLAN_ACCEPTANCE_STANDARD_CUTOFF`, a constant. Nothing here reads the clock
    or git history, so the same file gets the same verdict in any clone at any revision —
    the property a time-of-run switch cannot have. C1 and the `writing-plans` field it
    validates land in the same commit, so the cutoff is that commit's date and zero plans
    filed before today are ever in scope: **no warn phase, because there is nothing to warn
    about.**

    Scope is the plan *kind* only — the file `writing-plans` produces, discriminated by the
    four documented suffixes in `docs/plans/README.md`, never by guessing at content. Widen
    it past that and it reds on every future ledger, ruling record or handover file, which
    the "no warn phase" design above cannot excuse (Ruling 46 §2's own warning about a check
    that guesses).

    Legacy plans (filed before the cutoff) get **one aggregate note line**, not one warning
    each — Ruling 46 §2 took this from the same principle a hundred per-file lines would
    violate: a check nobody reads because it never says anything new is worse than no check.
    """
    plans_dir = ROOT / "plans"
    legacy = 0
    checked = 0
    for f in sorted(plans_dir.glob("*.md")):
        name = f.name
        if name == "README.md":
            continue
        if name.endswith(_PLAN_KIND_EXCLUDED_SUFFIXES):
            continue

        m = _PLAN_FILENAME_DATE.match(name)
        if not m:
            fail(
                f"docs/plans/{name}: not one of the four documented kind-suffixes "
                "(-ledger/-final-review/-verified/-handover) and carries no `YYYY-MM-DD-` "
                "date prefix either — docs/plans/README.md §Naming requires the prefix on "
                "every filed plan, and check 28 cannot classify or date this file without it"
            )
            continue

        filed = date.fromisoformat(m.group(1))
        if filed < PLAN_ACCEPTANCE_STANDARD_CUTOFF:
            legacy += 1
            continue

        checked += 1
        lines = f.read_text(encoding="utf-8").splitlines()
        heading_idx = next(
            (i for i, line in enumerate(lines) if _ACCEPTANCE_STANDARD_HEADING.match(line)),
            None,
        )
        if heading_idx is None:
            fail(
                f"docs/plans/{name}: no \"Acceptance Standard\" heading — every plan filed "
                f"on or after {PLAN_ACCEPTANCE_STANDARD_CUTOFF.isoformat()} must state one "
                "explicitly (delivery-process.md §5 step 4 / §6 step 1; field format in "
                ".claude/skills/writing-plans/SKILL.md)"
            )
            continue

        # Stop scanning at the next heading of any level; a bare heading followed
        # immediately by another heading is exactly the "implied, not defined" case.
        body_has_content = False
        for line in lines[heading_idx + 1 :]:
            if re.match(r"^#{1,6}\s", line):
                break
            if line.strip():
                body_has_content = True
                break
        if not body_has_content:
            fail(
                f"docs/plans/{name}: \"Acceptance Standard\" heading has no content before "
                "the next heading — a bare heading is \"implied\", not \"actually defined\" "
                "(delivery-process.md §5 step 4)"
            )

    if legacy:
        notes.append(
            f"{legacy} legacy plan(s) filed before "
            f"{PLAN_ACCEPTANCE_STANDARD_CUTOFF.isoformat()} exempted from check 28 "
            "(Ruling 46 — never retro-red-gated)"
        )
    notes.append(
        f"check 28: {checked} plan(s) filed on/after "
        f"{PLAN_ACCEPTANCE_STANDARD_CUTOFF.isoformat()} checked for an acceptance standard"
    )


def main() -> int:
    md = sorted(ROOT.rglob("*.md"))
    specs = sorted(ROOT.glob("specs/*.md"))

    # 1. relative links
    for f in md:
        for m in re.finditer(r"\[[^\]]*\]\(([^)#\s]+)(#[^)]*)?\)", f.read_text(encoding="utf-8")):
            target = m.group(1)
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            if not (f.parent / target).resolve().exists():
                fail(f"broken link in {f.relative_to(ROOT)}: {target}")

    # 2/3. requirement ids
    defined: dict[str, list[str]] = collections.defaultdict(list)
    for f in specs:
        for m in re.finditer(r"\*\*((?:FR|NFR)-[A-Z]+-\d+)\*\*", f.read_text(encoding="utf-8")):
            defined[m.group(1)].append(f.name)
    for rid, where in defined.items():
        if len(where) > 1:
            fail(f"{rid} defined in multiple specs: {where}")

    # A filed plan is written *before* the spec change it argues for, so it names the id it
    # intends to take — "Next free: `FR-DATA-53`" — which by definition is not yet defined.
    # That is an allocation note, not a citation, and docs/plans/ is the only place in the
    # suite where an undefined id is the correct thing to write.
    #
    # The exemption is deliberately narrow on both axes. It applies only under docs/plans/,
    # so a spec can never dodge this check by borrowing the phrase; and only to the ids
    # *after* the marker, so the real citations sharing that line are still checked. The
    # plans cite 116 distinct requirements between them — exempting the directory wholesale
    # would blind check 2 to all of them to accommodate one line.
    plans_dir = ROOT / "plans"
    referenced: dict[str, set[str]] = collections.defaultdict(set)
    for f in md:
        is_plan = f.is_relative_to(plans_dir)
        for line in f.read_text(encoding="utf-8").splitlines():
            marker = UNALLOCATED.search(line) if is_plan else None
            cited = line[: marker.start()] if marker else line
            for m in re.finditer(r"\b((?:FR|NFR)-[A-Z]+-\d+)\b", cited):
                referenced[m.group(1)].add(str(f.relative_to(ROOT)))
    for rid in sorted(set(referenced) - set(defined)):
        fail(f"{rid} referenced but never defined (in {sorted(referenced[rid])})")

    by_prefix: dict[str, list[int]] = collections.defaultdict(list)
    for rid in defined:
        prefix, num = rid.rsplit("-", 1)
        by_prefix[prefix].append(int(num))
    for prefix, nums in sorted(by_prefix.items()):
        missing = sorted(set(range(1, max(nums) + 1)) - set(nums))
        if missing:
            fail(f"{prefix} has numbering gaps: {missing}")

    notes.append(f"{len(defined)} requirements defined across {len(specs)} specs")

    # 4. open questions
    in_specs = set()
    for f in specs:
        in_specs |= set(re.findall(r"\*\*(OQ-[A-Z]+-\d+)\*\*", f.read_text(encoding="utf-8")))
    oq_file = ROOT / "open-questions.md"
    in_file = set(re.findall(r"\*\*(OQ-[A-Z]+-\d+)\*\*", oq_file.read_text(encoding="utf-8")))
    for q in sorted(in_specs - in_file):
        fail(f"{q} raised in a spec but not mirrored into open-questions.md")
    for q in sorted(in_file - in_specs):
        fail(f"{q} listed in open-questions.md but raised in no spec")
    # The verdict goes in the summary line, not just in the failure list (check 21's
    # pattern): a note reading "all mirrored" above a FAILED block hides the failure.
    unmirrored = len(in_specs - in_file) + len(in_file - in_specs)
    verdict = "all mirrored" if not unmirrored else f"**{unmirrored} not mirrored**"
    notes.append(f"{len(in_file)} open questions, {verdict}")

    # 5. ADRs
    adrs = {p.name.split("-")[0] for p in ROOT.glob("adr/0*.md")}
    corpus = "\n".join(f.read_text(encoding="utf-8") for f in md)
    for ref in sorted(set(re.findall(r"ADR-(\d{4})", corpus)) - adrs):
        fail(f"ADR-{ref} referenced but no file exists")

    # 6. spec sections
    for f in specs:
        heads = re.findall(r"^## \d+\.?\s*(?:—\s*)?(.+)$", f.read_text(encoding="utf-8"), re.M)
        lowered = [h.lower() for h in heads]
        for name in REQUIRED_SECTIONS:
            key = name.lower().split("(")[0].strip()
            if not any(key in h for h in lowered):
                fail(f"{f.name} missing required section: {name}")

    # 7. JSON schemas
    def no_dupes(pairs: list[tuple[str, object]]) -> dict[str, object]:
        seen = collections.Counter(k for k, _ in pairs)
        dupes = [k for k, c in seen.items() if c > 1]
        if dupes:
            raise ValueError(f"duplicate keys {dupes}")
        return dict(pairs)

    schema_root = ROOT / "contracts" / "schemas"
    schemas = sorted((ROOT / "contracts").rglob("*.json"))
    loaded: dict[pathlib.Path, object] = {}
    for f in schemas:
        try:
            loaded[f] = json.load(f.open(encoding="utf-8"), object_pairs_hook=no_dupes)
        except ValueError as exc:
            fail(f"{f.relative_to(ROOT)}: {exc}")

    # 8. $ref resolution

    def resolve_pointer(doc: object, fragment: str) -> bool:
        """Resolve a JSON Pointer fragment such as '/$defs/QuoteContext'."""
        cur = doc
        for part in fragment.lstrip("/").split("/"):
            part = part.replace("~1", "/").replace("~0", "~")
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return False
        return True

    def check_ref(ref: str, src: pathlib.Path) -> None:
        if ref.startswith(_ABS_PREFIX):
            tail = ref[len(_ABS_PREFIX):]
        elif ref.startswith("#"):
            if len(ref) > 1 and not resolve_pointer(loaded[src], ref[1:]):
                fail(f"{src.relative_to(ROOT)}: local $ref {ref} does not resolve")
            return
        elif ref.startswith(("http://", "https://")):
            return  # external, not our concern
        else:
            tail = ref
        target, _, fragment = tail.partition("#")
        path = (schema_root / target) if ref.startswith(_ABS_PREFIX) else (src.parent / target)
        path = path.resolve()
        if path not in loaded:
            fail(f"{src.relative_to(ROOT)}: $ref {ref} -> missing {target}")
        elif fragment and not resolve_pointer(loaded[path], fragment):
            fail(f"{src.relative_to(ROOT)}: $ref {ref} -> fragment does not resolve")

    def walk(node: object, src: pathlib.Path) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "$ref" and isinstance(value, str):
                    check_ref(value, src)
                else:
                    walk(value, src)
        elif isinstance(node, list):
            for item in node:
                walk(item, src)

    loaded = {f.resolve(): doc for f, doc in loaded.items()}
    for f in schemas:
        if f.resolve() in loaded:
            walk(loaded[f.resolve()], f.resolve())
    notes.append(f"{len(loaded)} JSON schemas parsed, $refs checked")

    # ------------------------------------------------------------------ 9-14
    spec_by_code = {
        "00": "00-overview.md", "01": "01-data-management.md",
        "02": "02-modelling.md", "03": "03-rating-engine.md",
        "04": "04-optimisation.md", "05": "05-monitoring.md",
        "06": "06-governance.md", "07": "07-platform.md",
    }
    spec_text = {f.name: f.read_text(encoding="utf-8") for f in specs}

    # 9. cross-spec section references, e.g. `01` §4.5  /  02 §3.2
    # `(?<![0-9-])` matters: without it the `02` inside a date like `2026-08-15` matches,
    # and any § reference within the next 24 characters is reported as a broken
    # cross-reference to `02`. It reads exactly like a real finding, which is the worst
    # kind of false positive.
    sec_re = re.compile(r"(?<![0-9-])`?(0[0-7])`?[^\n]{0,24}?§(\d+(?:\.\d+)*)")
    for f in md:
        for m in sec_re.finditer(f.read_text(encoding="utf-8")):
            code, sec = m.group(1), m.group(2)
            target = spec_by_code[code]
            body = spec_text.get(target, "")
            top = sec.split(".")[0]
            # a heading "## N." must exist; sub-sections may be "### N.M"
            if not re.search(rf"^#{{2,4}} {re.escape(sec)}[.\s]", body, re.M) and \
               not re.search(rf"^#{{2,4}} {re.escape(top)}\.", body, re.M):
                fail(
                    f"{f.relative_to(ROOT)}: reference to {code} §{sec} — "
                    f"no such section in {target}"
                )

    # 10. error-code ownership is exclusive
    owner: dict[str, str] = {}
    conflicts = 0
    code_re = re.compile(r"\*\*Error codes owned by this module:\*\*(.+?)(?:\n\n|###)", re.S)
    for f in specs:
        m = code_re.search(f.read_text(encoding="utf-8"))
        if not m:
            continue
        block = m.group(1)
        for cm in re.finditer(r"`([A-Z][A-Z0-9_]{3,})`(\s*\(re-raised from[^)]*\))?", block):
            code, reraised = cm.group(1), bool(cm.group(2))
            if reraised:
                continue  # explicitly borrowed from the owning module
            if code in owner and owner[code] != f.name:
                conflicts += 1
                fail(
                    f"error code {code} claimed by both {owner[code]} and "
                    f"{f.name} — annotate one as '(re-raised from `NN`)' or "
                    "give ownership to one module"
                )
            owner.setdefault(code, f.name)
    # The verdict goes in the summary line (check 21's pattern): a note reading
    # "ownership exclusive" above a FAILED block hides the failure.
    verdict = "ownership exclusive" if not conflicts else f"**{conflicts} conflicts**"
    notes.append(f"{len(owner)} error codes, {verdict}")

    # 11. DEP-1 build order: a module must not consume from a module to its right
    order = ["PLAT", "GOV", "DATA", "MODEL", "RATE", "OPT", "MON"]
    code_of = {"01": "DATA", "02": "MODEL", "03": "RATE", "04": "OPT",
               "05": "MON", "06": "GOV", "07": "PLAT"}
    for f in specs:
        code = f.name[:2]
        if code not in code_of:
            continue
        me = code_of[code]
        body = f.read_text(encoding="utf-8")
        m = re.search(r"### 7\.1 (?:This module )?[Cc]onsumes(.*?)### 7\.2", body, re.S)
        if not m:
            continue
        for row in m.group(1).splitlines():
            if not row.startswith("| `"):
                continue
            src = re.match(r"\| `(\d\d)", row)
            if not src or src.group(1) not in code_of:
                continue
            other = code_of[src.group(1)]
            if order.index(other) <= order.index(me):
                continue
            # DEP-1a: GOV's audit sink and permission check are cross-cutting interfaces
            if other == "GOV" and re.search(r"audit|permission|authoris|authoriz|RBAC", row, re.I):
                continue
            fail(
                f"{f.name}: DEP-1 violation — {me} consumes from {other}, "
                "which is to its right"
            )

    # 12. money discipline: *_minor fields must never be fractional.
    #: FR-OVR-20, not FR-OVR-7. FR-OVR-7 governs values and is scoped to the rating path and
    #: persisted rate tables, so it does not reach a diagnostic; the reserved *name* is
    #: FR-OVR-20 and is unscoped, which is the rule this check actually applies. It named
    #: FR-OVR-7 until 2026-08-24, when FR-OVR-20 was written down (OQ-OVR-11).
    money_re = re.compile(r'"(\w*_minor)"\s*:\s*(-?\d+\.\d+)')
    for f in list(md) + schemas:
        for m in money_re.finditer(f.read_text(encoding="utf-8")):
            fail(
                f"{f.relative_to(ROOT)}: {m.group(1)} written as fractional "
                f"{m.group(2)} (FR-OVR-20)"
            )

    # 13. glossary terms not redefined downstream
    def terms(body: str, section: str) -> set[str]:
        m = re.search(rf"^## {section}\..*?$(.*?)^## ", body, re.S | re.M)
        if not m:
            return set()
        return {t.strip().lower() for t in re.findall(r"^\| \*\*(.+?)\*\* \|", m.group(1), re.M)}
    canon = terms(spec_text["00-overview.md"], "2")
    for f in specs:
        if f.name == "00-overview.md":
            continue
        for t in terms(f.read_text(encoding="utf-8"), "2") & canon:
            fail(
                f"{f.name}: glossary term '{t}' is already defined in "
                "00-overview.md §2 — reference it, do not redefine"
            )

    # 14. workflow coverage per module
    #
    # Most requirements are property-level ("TLS 1.3", "normalise to snake_case") and a
    # workflow legitimately never cites them — journeys cite step-level requirements.
    # So raw orphan count is not a defect signal. What IS a defect is a module no
    # workflow exercises at all, or coverage collapsing for one module while others
    # hold. The floor catches both; it is deliberately low.
    coverage_floor = 0.10
    wf_text = "\n".join(f.read_text(encoding="utf-8") for f in ROOT.glob("workflows/*.md"))
    per_mod: dict[str, list[int]] = collections.defaultdict(lambda: [0, 0])
    for rid in defined:
        if rid.startswith("NFR-"):
            continue
        mod = rid.split("-")[1]
        per_mod[mod][1] += 1
        if rid in wf_text:
            per_mod[mod][0] += 1
    summary = []
    for mod in sorted(per_mod):
        hit, tot = per_mod[mod]
        ratio = hit / tot if tot else 1.0
        summary.append(f"{mod} {ratio:.0%}")
        if ratio < coverage_floor:
            fail(f"workflow coverage for {mod} is {ratio:.0%} ({hit}/{tot}), below the "
                 f"{coverage_floor:.0%} floor — no user journey exercises this module")
    notes.append("workflow coverage: " + ", ".join(summary))

    # 15. open-question rows have an owner and a recognised status
    check_open_question_columns()

    # 21. journey citations resolve to a declared interface (FR-OVR-17, OQ-OVR-6)
    #
    # `scope-audit.py --endpoints` compares a spec's §5.1 table against the published
    # contract. This is the same idea one level up: the **journeys** cite endpoints and
    # `pricing-core` functions, and a journey citing something no spec declares is drift
    # nothing else in this repository can see. `audit-docs.py` check 14's "workflow coverage"
    # measures whether a journey *mentions* a requirement id, which is a different and much
    # weaker question — the one plan review 2 found it was answering.
    #
    # It earned its place on the first run: wf-01 A8 cited `profile_version()`, and `01`
    # §5.2 was corrected to `profile_frame` / `profile_parquet` on 2026-08-15 without the
    # journey being updated.
    declared_paths: dict[tuple[str, tuple[str, ...]], str] = {}
    for f in specs:
        for line in f.read_text(encoding="utf-8").splitlines():
            row = _ENDPOINT_ROW.match(line)
            if not row:
                continue
            for path in (p for p in re.findall(r"`([^`]+)`", row.group(2)) if p.startswith("/")):
                for method in re.split(r"`?/`?", row.group(1)):
                    key = (method.strip("`"), _path_segments(path))
                    declared_paths.setdefault(key, f.name)

    declared_functions: dict[str, str] = {}
    for f in specs:
        for m in re.finditer(
            r"^(?:async )?def ([a-z_][a-z0-9_]*)\(", f.read_text(encoding="utf-8"), re.M
        ):
            declared_functions.setdefault(m.group(1), f.name)

    journeys = sorted(ROOT.glob("workflows/wf-*.md"))
    cited_paths = cited_functions = loose = undeclared = 0
    for f in journeys:
        body = f.read_text(encoding="utf-8")
        for m in re.finditer(r"`(GET|POST|PUT|PATCH|DELETE) ([^`]+)`", body):
            # A journey may show the request body after the path — `POST /x {"to":"y"}`.
            segments = _path_segments(m.group(2).split(" ")[0])
            key = (m.group(1), segments)
            cited_paths += 1
            if key in declared_paths:
                continue
            match = _placeholder_match(key, declared_paths)
            if match is not None:
                # A journey writes `/environments/prod/deployments` where `03` §5.1 declares
                # `/environments/{env}/deployments`, and the journey is **right** to be
                # concrete — which environment is deployed to is the step's content. So a
                # declared `{}` segment matches a literal one. Counted and reported rather
                # than silent: it is the one place this check is looser than an exact
                # comparison, and a reader should be able to see how often it is used.
                loose += 1
                continue
            undeclared += 1
            fail(
                f"{f.name}: cites `{m.group(1)} {m.group(2)}`, which no spec declares in "
                "its §5.1 REST API table (FR-OVR-17)"
            )
        for m in re.finditer(r"`([a-z_][a-z0-9_]*)\(\)`", body):
            cited_functions += 1
            if m.group(1) not in declared_functions:
                undeclared += 1
                fail(
                    f"{f.name}: cites `pricing-core` function `{m.group(1)}()`, which no "
                    "spec declares in its §5.2 interface block (FR-OVR-17)"
                )
    # The verdict goes in the summary line, not just in the failure list. A note reading
    # "all declared" above a `FAILED` block is the shape of thing this audit exists to catch.
    verdict = "all declared" if not undeclared else f"**{undeclared} undeclared**"
    notes.append(
        f"journey citations: {cited_paths} endpoints, {cited_functions} functions, "
        f"{verdict} ({loose} matched a declared path placeholder)"
    )

    # 22. every table row has its header's cell count. `CLAUDE.md` is included even though
    # the other checks scan `docs/` only: it is the most-read document here, it is full of
    # tables, and `docs.yml` already runs on a change to it.
    check_table_rows([*md, REPO / "CLAUDE.md"])

    # 24. the §5.3 route column agrees with the §5.6 canonical route column
    #
    # `00` §5.6 declares the canonical routes (FR-OVR-22); each module's §5.3 gives the
    # route of every view it builds. A route §5.6 declares for a module must appear in that
    # module's §5.3 — a §5.3 that drops or rewrites a canonical route is drift nothing else
    # sees. Routes, never view names: two named views on one route are two §5.3 rows
    # carrying the same route. A module's §5.3 legitimately carries detail routes the
    # inventory does not list, so the check is one-directional: §5.6 is canonical and a
    # mismatch is a §5.3 error (recorded 2026-08-27, `00` §5.6).
    def _norm_route(r: str) -> str:
        r = r.split("?", 1)[0].rstrip("/")
        return re.sub(r"\{([^}]+)\}", r":\1", r)

    def _route_rows(spec: pathlib.Path, sec: str) -> list[list[str]]:
        rows: list[list[str]] = []
        on = False
        for line in spec.read_text(encoding="utf-8").splitlines():
            if line.strip() == f"### {sec}" or line.startswith(f"### {sec} "):
                on = True
                continue
            if on and re.match(r"^#{2,4} ", line):
                break
            if on and line.startswith("|"):
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if cells and cells[0] != "View":
                    rows.append(cells)
        return rows

    def _row_routes(row: list[str], col: int) -> set[str]:
        return {_norm_route(p) for p in re.findall(r"`(/[^`]+)`", row[col])}

    overview = next(f for f in specs if f.name == "00-overview.md")
    canonical: dict[str, set[str]] = collections.defaultdict(set)
    for row in _route_rows(overview, "5.6"):
        if len(row) >= 3:
            canonical[row[2]].update(_row_routes(row, 1))
    for f in specs:
        if f.name == "00-overview.md":
            continue
        code = f.name[:2]
        s53: set[str] = set()
        for row in _route_rows(f, "5.3"):
            if len(row) >= 2:
                s53.update(_row_routes(row, 1))
        for route in sorted(canonical.get(code, set())):
            if route.endswith("/*"):
                prefix = route[:-1]
                if not any(r.startswith(prefix) for r in s53):
                    fail(
                        f"{f.name} §5.3: no route under `{route}` declared in `00` §5.6 "
                        f"(owner {code}) — fix {f.name} §5.3 (`00` §5.6 is canonical)"
                    )
            elif route not in s53:
                fail(
                    f"{f.name} §5.3: route `{route}` declared in `00` §5.6 (owner {code}) "
                    f"has no matching row — fix {f.name} §5.3 (`00` §5.6 is canonical)"
                )

    # 16-20. the working notes in docs/notes/
    check_notes(set(defined), in_file, adrs)

    # 30. the vacated .claude/notes/ tombstone: exactly the README plus the frozen
    # stub set, each stub byte-identical to its rendered template — Ruling 61.
    check_notes_tombstone()

    # 23. every spec §10 mirror row carries the register's status for that question
    check_open_question_mirror_status(specs)

    # 25. every F-nn finding id cited in docs/research/, docs/plans/ or a working note
    # resolves against the register, an archived phase register, or a closure record
    check_finding_citations()

    # 26. the process core extract's citations resolve in the process spec
    check_process_core_drift()

    # 27. the process core extract's recorded digest matches delivery-process.md's bytes
    check_process_core_digest()

    # 28. every filed plan dated on/after the cutoff states an acceptance standard
    check_plan_acceptance_standard()

    # 29. every docs/audit/register.md Decision cell conforms to its own header grammar
    check_register_grammar()

    for note in notes:
        print(f"  {note}")

    if failures:
        print(f"\nFAILED ({len(failures)}):")
        for msg in failures:
            print(f"  - {msg}")
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())