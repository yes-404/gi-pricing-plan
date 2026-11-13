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
 15. (retired by ADR 8449: the open-question mirror.)
 16-20. (retired by ADR 8449: the working notes are the frozen rfcs family.)
 21. Every endpoint and pricing-core function a workflow journey cites is declared
     in the owning module's §5.1 or §5.2 (FR-19, OQ-543).
 22. Every markdown table row has its own header's cell count — catching a literal
     `|` inside a cell, which shifts every column after it while still rendering.
 23. (retired by ADR 8449: the open-question mirror.)
 24. Every route `00` §5.6 declares as canonical for a module appears in that module's
     own §5.3 view table (FR-25); §5.6 is canonical, so a mismatch is a §5.3 error.
 25. (retired by ADR 8449: it audited citations between frozen record families only.)
 26. Every `source` citation in docs/process/delivery-process.core.json resolves to a
     real section, or numbered step, of docs/process/delivery-process.md (RFC-895 §3).
 27. The process core extract's recorded digest (`meta.derived_from_digest`) matches the
     current bytes of docs/process/delivery-process.md, paired with the commit it was last
     reconciled against (`meta.verified_against_tree`) — the other half of check 26's own
     "cheap half of a drift check" (RL-905).
 28. (retired by ADR 8449: the plan acceptance standard; plans are a frozen family.)
 29. (retired by ADR 8449: the findings register is frozen; register-lint.py is removed.)


RFC-937
(docs/rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md)
§1.11 — one id per governed thing.
Checks 30-39 below, path-scoped to `_ID_SCOPE_ROOTS` until the migration (Slice W37-6)
widens it to the whole corpus (docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md,
Slice W37-4, 2026-09-02). **Slot 30 changed identity on this date**: it held
`check_notes_tombstone` (the vacated `.claude/notes/` tombstone check, RL-951); RFC-937
§5.5 resolves the collision between that check and this note's own header check — both
numbered 30 — by replacing the former rather than renumbering either
(`check_notes_tombstone` -> `check_redirects`, moving to slot 36, which is what its job
becomes: watching REDIRECTS.csv instead of the tombstone stubs it replaces). The number 30
is not reused for two things; `check_notes_tombstone`'s protective job over the tombstone
stubs ends with this commit, by that same resolution, until W37-6 deletes the stubs
entirely.
 30. Header present and parseable on every file in scope; no unknown field; required
     fields per family, read from docs/_templates/ (RL-981) — never transcribed from
     RFC-937 §1.5's own parenthesis, which diverges from the templates in both directions.
 31. Header `id` prefix and integer equal the filename's; directory equals family;
     numbers unique in scope (contiguity retired by ADR 8449); `created` non-decreasing
     with the number.
     `docs/_templates/` is exempt by path (RFC-937 §1.4).
 32. Every `<PREFIX>-<n>` in prose resolves in docs/INDEX.md and its prefix matches the
     number's family; no padded id outside a link target; a link's text and target cite
     the same id. Gated on docs/INDEX.md existing (pre-migration there is no citation
     corpus, and document-ids.md's own illustrative ids would otherwise false-positive).
 33. `supersedes`/`superseded_by` symmetric; `status:` is in the standard's vocabulary and
     in the family's own subset of it; the map-plan roll-up raise surfaced rather than
     swallowed (RL-983 — doc-index.py's precedence table has no catch-all).
 34. Freeze: a frozen family's diff against its merge-base touches only `status:` (forward
     only), `superseded_by:`, an appended `corrected_by:` entry, or (ledgers) an appended
     `plans:` entry (DP-7); every `corrected_by:` entry is a record whose `corrects:` names
     this file.
 35. `owner:` is a role filename under .claude/roles/, or `maintainer`, and one the
     directory's README.md permits where that README declares a permitted-owner list.
     (ADR 8449 retired the rest: F83's register of unstampable files and the stamping
     completeness clause. The original text follows, kept for the record:)
     F83's register of files that cannot carry a header at all (60 generated
     artifacts under docs/ in formats with no comment syntax, 3 unparseable vendored
     SKILL.md manifests, 2 more surfaced by the check itself) reconciled against
     RFC-937's stamp set by name — every entry citing its reason and its ruling
     (condition 1), and the register held equal to the tree so it cannot grow silently
     (condition 2). Naming, never a total: two errors that cancel pass a total-only
     check, which is RL-985's reason and `.claude/skills/docs-audit`
     §"a total validates the total, and nothing else".
 36. (ADR 8449: scoped to the governed families; a legacy form the change introduces
     fails, a pre-existing one is counted.)
     Redirects (renamed from `check_notes_tombstone`, see above): every `was:` has a
     REDIRECTS.csv row; every row's target exists; no pre-migration id or path form
     survives outside REDIRECTS.csv and `was:` lines (RL-988/DP-2) — one shared
     pattern-and-exclusion constant, reused unscoped by RFC-937 §7 acceptance item (d)
     once the migration lands.
 37. Shape: a document carries every `##` section its family's template body declares —
     the ten-section spec rule, generalised.
 38. (retired by ADR 8449.)
     Loop signal, warn-only — never fails the gate. Notes only in S1: no PL-/RS-/RFC-
     population exists in scope yet to check coverage, freeze-gate dates or superseded/
     retired citations against.
 39. (retired by ADR 8449: docs/INDEX.md is a frozen citation resolver, no longer regenerated.)
 40. Every fence in docs/specs/ declares a language, and every `json` block declares
     `schema=<Class>` or `illustrative` and parses when classed (FD-1381). Validation
     against model-schema is tests/test_spec_examples.py's, so this script stays stdlib.

Usage: python3 scripts/audit-docs.py
"""
from __future__ import annotations

import collections
import csv
import functools
import hashlib
import importlib.util
import itertools
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import types
from collections.abc import Callable, Collection, Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from typing import Final

REPO = pathlib.Path(__file__).resolve().parent.parent
ROOT = REPO / "docs"


def migrated_tree() -> bool:
    """True on a tree the RFC-937 id migration has run over.

    **Why a sentinel and not a flag.** These parsers have to read the corpus on *both*
    sides of a one-way migration commit: this file lands on `main` before the migration
    runs (RL-1043 §3's carve-out — "any H row without which `audit-docs.py` finds zero
    requirements lands with the run"), so a parser hard-coded to the post-migration
    shape would red `main` on the day it merged, and one hard-coded to the pre-migration
    shape reports a **vacuous pass** — every count zero, exit code 0 — the moment the
    migration lands. Neither is acceptable; the population has to be discovered.

    **The predicate is the two artifacts only the migration creates**: `docs/INDEX.md`
    (generated by `doc-index.py`) and `docs/REDIRECTS.csv`. Checks 32, 36 and 39 already
    keyed their own pre-migration skips on exactly these two files; this names the
    predicate once instead of spelling it three ways.
    """
    return (ROOT / "INDEX.md").is_file() and (ROOT / "REDIRECTS.csv").is_file()


def _first_dir(*candidates: pathlib.Path) -> pathlib.Path:
    """The first candidate that is a directory, else the first candidate.

    Returning the first candidate rather than `None` when none exists keeps the caller's
    "this root is unconditionally present, its absence is an error" failure message
    pointing at the location the tree is *supposed* to have (`check_notes`'s docstring).
    """
    for path in candidates:
        if path.is_dir():
            return path
    return candidates[0]


def _first_file(*candidates: pathlib.Path) -> pathlib.Path:
    """The first candidate that is a file, else the first candidate."""
    for path in candidates:
        if path.is_file():
            return path
    return candidates[0]


#: The findings register: `docs/findings/register.md` pre-migration, `docs/findings/register.md`
#: after it (RFC-937 §5.2 — the two registers merge into one). Written as a *constant* and
#: not spelled inline at each use, because the migration rewrites the path **string** in this
#: file's own messages while leaving a `ROOT / "audit" / "register.md"` pathlib join
#: untouched: post-migration the un-fixed script printed "no docs/findings/register.md —
#: check 29 skipped" while reading `docs/findings/register.md`. The message moved, the parser
#: did not.
REGISTER = _first_file(ROOT / "audit" / "register.md", ROOT / "findings" / "register.md")
_ABS_PREFIX = "https://contracts.gi-pricing.dev/"
# docs/plans/ only: ids listed after this marker are being allocated, not cited. See check 2.
UNALLOCATED = re.compile(r"next free\s*:", re.IGNORECASE)

#: Requirement, open-question and dependency id **bodies**, accepting both the pre-migration
#: module-scoped form (`FR-154`) and the post-migration global-sequence form
#: (`FR-1187`, RFC-937 D2). The optional `[A-Z]+-` segment is the whole difference.
#:
#: These exist as named constants because the same shape is parsed at eleven sites, and after
#: the migration every one of them matching nothing is not a failure — it is a **pass over an
#: empty population**: "0 requirements defined across 8 specs", printed above `All checks
#: passed`. One spelling missed here is one summary line that lies. Measured on a migrated
#: snapshot of `e97b97a`: 533 requirements and 118 open questions became 0 and 0, and the
#: script still exited 0 on those two checks.
#:
#: Deliberately *not* used by check 26's legacy-form sweep (`_LEGACY_FORMS`), which has to
#: keep matching the scoped form and only the scoped form — that is the form it exists to
#: find.
#: **One regime per tree, chosen from the tree.** The two forms are not both accepted at
#: once: on an un-migrated tree the global form appears only as *illustration* — RFC-937 §3's
#: "Today | After" table and `document-ids.md`'s worked examples write `FR-1187` to show what
#: the migration will produce — and a parser accepting both reads those as citations of
#: requirements no spec defines. That is the failure mode this repository has hit repeatedly:
#: a check that cannot tell a document *defining* an id form from one *using* it. Selecting
#: the regime removes the ambiguity instead of carving out the documents that trip it.
_REQ_ID_BODY = r"(?:FR|NFR)-\d+" if migrated_tree() else r"(?:FR|NFR)-[A-Z]+-\d+"
_OQ_ID_BODY = r"OQ-\d+" if migrated_tree() else r"OQ-[A-Z]+-\d+"
#: A requirement id defined in a spec: bold, the form `spec-change` mandates.
_REQ_DEFINED = re.compile(r"\*\*(" + _REQ_ID_BODY + r")\*\*")
#: A requirement id cited anywhere.
_REQ_CITED = re.compile(r"\b(" + _REQ_ID_BODY + r")\b")
#: The pre-migration, module-scoped spelling only -- the discriminator between the two
#: numbering regimes in check 3.
_SCOPED_REQ_ID = re.compile(r"(?:FR|NFR)-[A-Z]+-\d+")
_OQ_DEFINED = re.compile(r"\*\*(" + _OQ_ID_BODY + r")\*\*")
_OQ_CITED = re.compile(r"\b(" + _OQ_ID_BODY + r")\b")
#: An open-question row's leading cell in `open-questions.md` or a spec §10 mirror table.
_OQ_ROW = re.compile(r"\| (?:~~)?\*\*(" + _OQ_ID_BODY + r")\*\*")
#: An ADR citation. Pre-migration files are `docs/adrs/0001-*.md` cited `ADR-703`;
#: post-migration they are `docs/adrs/ADR-00004-*.md` cited `ADR-4` (RFC-937 D6 — citations
#: unpadded, filenames padded to five). The old `ADR-(\d{4})` pattern reads the *first four*
#: digits of a five-digit padded id, so a real five-digit citation shaped `ADR-0NNNx` was
#: parsed as a citation of the schematic four-digit form `ADR-0NNN` and check 5 failed with
#: "ADR-0NNN referenced but no file exists" (respelled schematically, 2026-09-04, Ruling
#: 103 §5.1's fence clause extended to row (d): the literal digit form is itself a §7(d)
#: alternative match) — a real-looking failure manufactured entirely by the width of the
#: pattern. Matching
#: `0*(\d+)` with a boundary and comparing **integers** is width-agnostic in both
#: directions. **`ADR-999` rather than a real ADR**, deliberately: highest allocated is
#: `ADR-10`, and citing a real one here would itself be an `RFC-937` §7(e) violation
#: (RL-1044's four conjuncts) — this comment commenting on its own input, the same
#: shape §5.5 already fixed in this row's own test fixtures (`RL-09999`/`PL-09998`).
#: The `[1-9]` first digit is not cosmetic: with `0*(\d+)` the pattern matches the literal
#: text `ADR-0[0-9]{3}` — RFC-937 §7(d)'s own grep pattern, written in prose — as a
#: citation of "ADR-0", and check 5 then fails on a document that cites no ADR at all.
#: Ids are allocated from 1, so a leading run of zeros followed by nothing is never one.
_ADR_CITED = re.compile(r"\bADR-0*([1-9]\d*)\b")
#: An ADR *filename* in either layout: `0001-pricing-core-….md` or
#: `ADR-00004-pricing-core-….md`. The number is the only part compared.
_ADR_FILE = re.compile(r"^(?:ADR-)?0*(\d+)-")
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

    Needed because a journey is concrete where the spec is general — WF-701 deploys to `prod`,
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

def check_table_rows(md: list[pathlib.Path]) -> None:
    r"""Check 22: every table row has as many cells as its own header.

    The defect this catches is a literal `|` inside a table cell. GFM decides cell
    boundaries **before** it parses anything inline, so a pipe inside a code span still
    splits the row — `` `rows | parquet` `` silently becomes two cells, and every column
    after it shifts right. The row still renders, which is why nothing noticed: the table
    looks intact and the last cell's content has quietly moved into a column that means
    something else. Escaping (`` `rows \| parquet` ``) is the only fix, and it works inside
    a code span even though a backslash escape normally does not.

    Found 2026-08-18 in two rows written the same day — `03` FR-232 and OQ-616's
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
            cells = _docid.table_rows.cell_count(line)
            if header_cells is None:
                header_cells = cells
                continue
            if cells != header_cells:
                where = f"{f.relative_to(REPO)}:{lineno}"
                offenders = re.findall(
                    rf"`[^`]*{_docid.table_rows.UNESCAPED_PIPE.pattern}[^`]*`", line
                )
                detail = f" — unescaped pipe in {offenders[0]}" if offenders else ""
                fail(
                    f"check 22: table row has {cells} cells, its header has {header_cells} "
                    f"({where}){detail}"
                )


#: `F6`, `F26`, or the workstream-scoped `F-W9-1` / `F-W10-1-1` a phase-boundary carry-forward
#: uses — the findings register's own id shape, confirmed against every row in
#: `docs/findings/register.md` and `docs/audit/phases/*/register.md`.
#: The `FD-<n>` alternative is RFC-937 D7's post-migration form (`docs/findings/FD-0nnnn-*.md`,
#: cited `FD-93`). Listed first so the alternation prefers it: `F(?:…|\d+)` would otherwise
#: match the bare `F` of nothing at all, but more importantly a reader must not have to
#: re-derive which branch wins.
_FINDING_ID = r"(?:FD-0*\d+|F(?:-W\d+-\d+(?:-\d+)?|\d+))"
#: The register's own citation convention: a finding id in parentheses, immediately after the
#: text it concerns — `` `RL-882's acceptance-test premise (F32)` ``. See
#: `check_finding_citations`'s docstring for why a bare `F1` is deliberately not matched.
_FINDING_CITED = re.compile(r"\((" + _FINDING_ID + r")\)")
#: A file defining its own local, private findings — a heading (`## F1 — …`), a ledger
#: table's own first cell (`| F1 | … |`, the shape both `track-a-findings.md` and every
#: archived phase register use), or a bold paragraph lead-in (`**F-W11-1-2 — … .**`, the
#: shape
#: `docs/plans/PL-00846-wk-671-slice-1-evaluator-core-its-prerequisites-and-the-latency-harness.md`
#: uses for its own four findings).
_FINDING_HEADING = re.compile(r"^#{1,6}\s+(" + _FINDING_ID + r")\b", re.M)
_FINDING_TABLE_CELL = re.compile(r"^\|\s*(" + _FINDING_ID + r")\s*\|", re.M)
_FINDING_BOLD_LEAD = re.compile(r"^\*\*(" + _FINDING_ID + r")\b", re.M)


PROCESS_SPEC = REPO / "docs" / "process" / "delivery-process.md"
PROCESS_CORE = REPO / "docs" / "process" / "delivery-process.core.json"

#: `§7`, or `§5.4` for step 4 of §5's numbered list. `§N.M` is a *step*, not a `###`
#: subsection — `delivery-process.md` has no `###` headings at all, so a reader who assumed
#: subsections would report every step citation as dangling.
_CITATION = re.compile(r"§(\d+)(?:\.(\d+))?")


def check_process_core_drift() -> None:
    """26. Every `source` citation in the process core extract resolves in the process spec.

    `docs/process/delivery-process.core.json` is the machine-readable extract of
    `delivery-process.md` (RFC-895). **The markdown is authoritative and the extract is
    derived**, so an extract citing a section that does not exist means the extract is
    wrong — never the spec. The check is one-directional for that reason.

    This is the cheap half of a drift check, and it is the half that catches the failure
    which motivated the whole proposal: at `6f77abb` the process spec's own back-reference
    named `CLAUDE.md` §12 for a pointer that lives in §15, and no gate in the repository
    could see it. A citation that *resolves* is not proof the cited text still says what the
    citer thinks (`RFC-779`); a citation that does **not** resolve is proof of drift, with
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
                "check 26: docs/process/delivery-process.core.json is missing, but "
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
        fail(f"check 26: docs/process/delivery-process.core.json is not valid JSON: {exc}")
        return

    # The authority rule (RFC-895 §3) enforced on the artifact that claims it, rather than
    # only stated in the prose beside it.
    meta = core.get("meta", {})
    if meta.get("authoritative") is not False:
        fail(
            "check 26: process core `meta.authoritative` must be `false` — the markdown "
            f"spec is authoritative and the extract is derived (RFC-895 §3); found "
            f"{meta.get('authoritative')!r}"
        )
    derived = meta.get("derived_from")
    if not derived or not (REPO / derived).is_file():
        fail(
            f"check 26: process core `meta.derived_from` names {derived!r}, which is not "
            "a file in this repository — the extract must say what it is derived from"
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
                f"check 26: process core: `source` value {src!r} cites no § section — "
                "every block must name the spec section it was extracted from (RFC-895 §3)"
            )
            continue
        for section, step in found:
            checked += 1
            if section not in steps:
                fail(
                    f"check 26: process core cites §{section} (in {src!r}), but "
                    f"delivery-process.md has no `## {section}.` heading — the extract is "
                    "derived, so fix the extract, not the spec"
                )
            elif step and int(step) > steps[section]:
                fail(
                    f"check 26: process core cites §{section}.{step} (in {src!r}), but "
                    f"§{section} has only {steps[section]} numbered steps — `§N.M` means "
                    "step M of that section's list, and the spec has no `###` subsections"
                )

    if not checked and not uncited:
        fail(
            "check 26: process core carries no `source` citations at all — every block "
            "must cite the spec section it came from, which is what makes drift "
            "detectable (RFC-895 §3)"
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
    theoretical — at the moment this check was proposed (RL-905,
    `docs/plans/2026-08-30-nt-0014-q1-q3-q4-rulings.md`), `delivery-process.md` had taken two
    commits past the extract's only commit, including one that added two normative rules to
    the very section (§15) a guard block cites, and check 26 stayed green throughout.

    This is the other half. `meta.derived_from_digest` records a `sha256:` digest of the
    exact bytes of `meta.derived_from` (`delivery-process.md`) as read at the last
    reconciliation, paired with the commit that reconciliation happened at
    (`meta.verified_against_tree`, already present on the artifact — RL-905 makes it
    load-bearing for the first time). Comparing prose to JSON semantically is not buildable;
    comparing "the source has not moved since a human last reconciled the extract against
    it" is exactly this — three lines, and the check that actually forces the reconciliation.

    The pairing with a commit is not decoration (RL-905 §2): a bare digest mismatch says
    only "it changed", but the recorded commit lets the failure message name the exact range
    a session should read — `git diff <verified_against_tree>..HEAD -- delivery-process.md`
    — the difference between re-reading the diff and blindly bumping a hash.

    One-directional like check 26 and for the same reason: the markdown is authoritative
    (`meta.authoritative` is `false`), so a mismatch is always the extract falling behind,
    never the spec being wrong. Known cost, accepted per the ruling: this reds on every edit
    to the process spec, including a typo — the right price for a forced re-read.

    Numbered 27, the number RL-905 §3 reserved (free at `1407e09`); slice F took 28,
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
            "check 27: process core `meta.verified_against_tree` is missing or empty — "
            "the digest must be paired with the commit it was taken at (RL-905 §2), "
            "so a future mismatch can name the exact range to read"
        )

    if not recorded_digest:
        fail(
            "check 27: process core `meta.derived_from_digest` is missing — RL-905 "
            "requires a `sha256:`-prefixed digest of the exact bytes of "
            "`meta.derived_from` (delivery-process.md), recorded at the commit it was "
            "last reconciled against"
        )
        return

    if not recorded_digest.startswith("sha256:"):
        fail(
            f"check 27: process core `meta.derived_from_digest` {recorded_digest!r} is "
            "not `sha256:`-prefixed — RL-905 specifies a sha256 digest of the exact "
            "bytes"
        )
        return

    actual_digest = "sha256:" + hashlib.sha256(PROCESS_SPEC.read_bytes()).hexdigest()
    if recorded_digest != actual_digest:
        fail(
            f"check 27: process core `meta.derived_from_digest` ({recorded_digest}) "
            f"does not match the current bytes of delivery-process.md ({actual_digest}) "
            f"— the spec has changed since the extract was last reconciled at "
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


#: The date C1 and the `writing-plans` acceptance-standard field land together (RFC-895 §2,
#: RL-906 — `docs/rulings/RL-00906-q3-never-retro-red-gate-adopted-warn-until-the-format-lands-red-
#: thereafter-rejected-as-the-mechanism.md` RL-906). A constant, not
#: read from the clock or git history: the verdict must be a property of the plan's own
#: filename, reproducible in any clone at any revision, never of when the check happens to
#: run. **Permanent once landed, the same way a check number is (`CLAUDE.md` §5) — do not
#: move it forward to "catch up" a plan filed between this date and today.**
PLAN_ACCEPTANCE_STANDARD_CUTOFF = date(2026, 8, 31)

#: docs/plans/README.md's four file kinds: the plan itself carries no suffix; these four do,
#: and none of them declares an acceptance standard of their own (RL-906 §2). A filename
#: not matching one of these and not carrying a `YYYY-MM-DD-` prefix is a naming defect the
#: check refuses outright, rather than silently guessing which kind it is.
_PLAN_KIND_EXCLUDED_SUFFIXES = ("-ledger.md", "-final-review.md", "-verified.md", "-handover.md")
_PLAN_FILENAME_DATE = re.compile(r"^(\d{4}-\d{2}-\d{2})-")
#: The post-migration equivalent of `_PLAN_KIND_EXCLUDED_SUFFIXES`: a `PL-` document whose
#: `kind:` is terminal (RFC-937 §1.6 -- a review is the auditor's verdict, a handover is
#: the executor's) declares no acceptance standard of its own, exactly as RL-906 §2 says
#: of `-final-review`/`-verified`/`-handover`. `-ledger` has no counterpart here: a ledger
#: became its own `LG-` family under `docs/ledgers/` and is not a plan at all.
_PLAN_TERMINAL_KINDS = frozenset({"review", "handover"})
_ACCEPTANCE_STANDARD_HEADING = re.compile(r"^#{1,6}\s+.*acceptance standard", re.IGNORECASE)


####################################################################################
# RFC-937 checks 30-39 — one id per governed thing.
#
# docs/rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-
# layout-and-roles-per-family.md §1.11 is the table these implement; each
# function's docstring cites the row it is. Every one of them reads the shared parser
# from `scripts/_docid.py` (loaded by path below, the same idiom `_load_register_lint`
# above already uses for check 29's dependency) rather than redefining any of it — that
# module is W37-2's, "owned by this slice; W37-3 and W37-4 import it and do not redefine
# it" (the map plan's own words). `scripts/doc-index.py` is consumed the same way, only
# where a check needs its rollup or corpus-building logic specifically (check 33).
####################################################################################

_DOCID_PATH: Final = REPO / "scripts" / "_docid.py"
_DOC_INDEX_PATH: Final = REPO / "scripts" / "doc-index.py"


def _load_module(name: str, path: pathlib.Path) -> types.ModuleType:
    """Load a `scripts/` module by path — required for every hyphenated filename here
    (`doc-index.py` is not a legal `import` target), and used for the underscore-leading
    `_docid.py` too so both loads go through one helper.

    Bytecode caching suppressed for this one `exec_module` call — see `doc-id.py`'s own
    `_load_module` (the sibling copy this one was copied from) for why: when this module
    is itself loaded by path from inside a `migrate --verify` snapshot
    (`doc-id.py`'s `_load_audit_docs`), this call writes a `.pyc` into that snapshot's
    `scripts/__pycache__/`, which a whole-tree walk not aware of `.gitignore` (`doc-id.py`'s
    `_iter_tree_files`) would otherwise read back as new migration output.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Registered before `exec_module`: `_docid.py`'s `@dataclass` classes need
    # `sys.modules[cls.__module__]` to resolve at class-creation time (the same reason
    # `tests/test_doc_id.py`'s own loader does this).
    sys.modules[spec.name] = module
    previous_dont_write_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous_dont_write_bytecode
    return module


_docid = _load_module("_docid", _DOCID_PATH)
_frozen = _load_module("_frozen", REPO / "scripts" / "_frozen.py")


def _is_frozen_file(path: pathlib.Path) -> bool:
    """True for a file under a frozen record path (`scripts/_frozen.py`)."""
    try:
        return bool(_frozen.is_frozen(path.relative_to(REPO).as_posix()))
    except ValueError:
        return False
_doc_index = _load_module("_doc_index_for_audit_docs", _DOC_INDEX_PATH)

#: Roots checks 30-39 apply to. In W37-4 this is the set of paths that exist *after* the
#: standard lands and *before* the migration; W37-6 replaces it with the whole corpus in the
#: same commit that migrates, which is D14's "enforcement red from the migration PR".
def _id_scope_roots() -> tuple[pathlib.Path, ...]:
    """The roots checks 30-39 apply to, chosen from what is on disk.

    **Before the migration** this is the set of paths that exist once the standard has
    landed and nothing has moved yet: the templates and `document-ids.md` itself.

    **From the migration commit onward it is the whole corpus** — this function's own
    predecessor comment said so in as many words ("WK-978-6 replaces it with the whole
    corpus in the same commit that migrates"), and it is D14, *enforcement red from the
    migration PR*, because there is no population to phase in. Left un-widened, checks
    30-39 report `1 governed document(s) checked in scope` on a fully migrated tree of
    ~460 stamped documents: nine checks, every one green, every one over a population of
    one. That is the vacuity RL-1043 §3 names, and an exit code of 0 is exactly what it
    produces.

    The four post-migration roots are **not chosen here.** They are the tuple
    `tests/test_audit_docs_ids.py::_widened_roots` already models the widened scope with,
    and which the F87 test asserts reaches every file on the F83 exemption register. Naming
    a different set here would make the enforced scope and the scope that test proves
    complete two different things — the drift F87 exists to prevent.
    """
    if migrated_tree():
        return (
            ROOT,
            REPO / ".claude" / "roles",
            REPO / ".claude" / "skills",
            REPO / ".claude" / "agents",
        )
    return (ROOT / "_templates", ROOT / "process" / "document-ids.md")


_ID_SCOPE_ROOTS: Final = _id_scope_roots()

_TEMPLATES_DIR: Final = ROOT / "_templates"


def _id_scope_documents(
    roots: Sequence[pathlib.Path] | None = None,
) -> list[pathlib.Path]:
    """Every real *governed-document* file under the checks-30-39 scope roots — never
    `_templates/` itself, which checks 30 and 37 read as a field-policy and shape
    *source* (RL-981), not as a document to validate as one: a template's placeholder
    content (`created: YYYY-MM-DD`, `id: PL-NNNNN`) is not valid `Header` content and is
    not supposed to be — the same reason `_templates/` is exempt from check 31 "by path"
    (RFC-937 §1.4) extends to every check in this family that validates a document
    *instance* rather than reading the templates as data.

    `roots` defaults to `None`, resolved to the module-level `_ID_SCOPE_ROOTS` *inside*
    the function body rather than as the parameter's own default value — a default value
    is bound once, at function-definition time, which would make a test's runtime
    monkeypatch of `_ID_SCOPE_ROOTS` invisible to every caller (including every
    `check_*` function here) that calls this with no argument. Resolving it as a
    statement instead makes every no-argument call see whatever `_ID_SCOPE_ROOTS`
    currently names, which is what a broken-input test needs to be able to redirect.

    A **directory** root is expanded by `_docid.stamp_set_files`, the filesystem face of
    RFC-937 §4 step 5's stamp-set predicate — not by a markdown glob. That is `F87`: this
    function used to expand a directory with `rglob("*.md")`, so widening the roots
    reached no non-markdown file at all and 62 of the 65 files on the F83 exemption
    register stayed invisible to checks 30-39 however wide the roots were drawn. The glob
    was the gate, not the roots. Sharing the predicate with `nt0019_stamp_set` — one
    definition in `_docid`, not two spellings here — is what keeps the enforced scope and
    the reconciled corpus from drifting apart again, and
    `test_the_two_stamp_set_consumers_read_one_definition` holds them to it.

    A **file** root is still appended verbatim, whatever its extension: a caller naming a
    single path is naming a document, and there is no directory whose rule could narrow
    it.
    """
    if roots is None:
        roots = _ID_SCOPE_ROOTS
    files: list[pathlib.Path] = []
    for root in roots:
        if root == _TEMPLATES_DIR:
            continue
        if root.is_file():
            files.append(root)
        elif root.is_dir():
            files.extend(_docid.stamp_set_files(root, REPO))
    # `_templates/` is exempt **by path** (RFC-937 §1.4, RL-981) — this function's own
    # docstring says so, and the `root == _TEMPLATES_DIR` branch above enforced it only when
    # the templates directory was named as a root in its own right. Once a root *above* it is
    # widened to `docs/`, `_docid.stamp_set_files` reaches all thirteen templates and every
    # check in this family validates a field-policy *source* as a document *instance*: 13
    # check-30 failures for placeholder content (`created: YYYY-MM-DD`, `id: PL-NNNNN`) that
    # is deliberately not valid header content. The exemption has to be applied to the file,
    # not to the root, the moment the roots can contain the directory rather than be it.
    #
    # A caller naming `_templates/` itself is naming exactly what it wants, and is honoured.
    if _TEMPLATES_DIR in roots:
        files = sorted(set(files))
    else:
        files = sorted(f for f in set(files) if not f.is_relative_to(_TEMPLATES_DIR))
    # The W37-11 residue ceiling record (`_docid.W37_11_RECORD_PATH`) is exempt
    # **unconditionally**, by path, never honoured even when a caller names it directly —
    # unlike `_templates/`, there is no scenario where validating it as a governed
    # document instance (checks 30/32/33/35/36) is the right question. Checks 32 and 36
    # both draw their corpus from this function (`check_citations`'s `for path in
    # _id_scope_documents()`; `sweep_legacy_forms`'s `_sweep_legacy_form_hits(
    # _id_scope_documents())`), so one exclusion here covers both — the record's own
    # legacy-path/token quotations would otherwise be counted as the very residue it
    # exists to disclose (deputy's condition on PR #756).
    w37_11_record = REPO / _docid.W37_11_RECORD_PATH
    # ADR 8449: a frozen record is not audited; it is the evidence of what was believed.
    return [f for f in files if f != w37_11_record and not _is_frozen_file(f)]


def _governed_documents() -> list[pathlib.Path]:
    """The documents checks 30, 35 and 36 apply to: the families the new frame still
    governs (`_frozen.is_governed`: docs/specs, docs/adrs, docs/workflows and the kept
    process pages) and nothing else. Skill front matter, generated contracts and the frozen
    records are out by family, never by an exemption list (ADR 8449, maintainer's residue
    ruling)."""
    return [f for f in _id_scope_documents() if _frozen.is_governed(_repo_rel(f))]


def _repo_rel(path: pathlib.Path) -> str:
    """`path` relative to the repository (or to the docs root's parent, for a fixture tree)."""
    for base in (REPO, ROOT.parent):
        try:
            return path.relative_to(base).as_posix()
        except ValueError:
            continue
    return path.as_posix()


_BASE_REF: Final = os.environ.get("AUDIT_DOCS_BASE", "origin/main")
_freeze_check: types.ModuleType | None = None


def _touched_paths() -> set[str] | None:
    """Paths this change touches (`<base>...HEAD`), from freeze-check.py's own range code
    (one range implementation, not two); `None` when the diff cannot be computed."""
    global _freeze_check
    if _freeze_check is None:
        scripts = pathlib.Path(__file__).resolve().parent  # this script's own directory
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        _freeze_check = _load_module("_freeze_check_for_audit_docs", scripts / "freeze-check.py")
    try:
        _head, paths = _freeze_check.changed_paths(_BASE_REF, str(REPO))
    except (subprocess.CalledProcessError, OSError):
        return None
    return set(paths)


def _text_at_base(rel: str) -> str | None:
    """`rel` as it was at the merge-base of `<base>...HEAD`, or `None` if it did not exist."""
    out = subprocess.run(
        ["git", "-C", str(REPO), "show", f"{_merge_base()}:{rel}"], capture_output=True, text=True
    )
    return out.stdout if out.returncode == 0 else None


def _merge_base() -> str:
    return subprocess.run(
        ["git", "-C", str(REPO), "merge-base", _BASE_REF, "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def _residue_gate(
    check: str,
    found: Mapping[str, Sequence[tuple[str, str]]],
    at_base: Callable[[pathlib.Path, str], Collection[str]],
) -> None:
    """Fail only what this change introduces; count what was already there.

    `found` maps a governed file to its `(key, message)` violations at HEAD. A violation is
    *pre-existing* when its file exists at the merge-base of `<base>...HEAD` and either the
    change does not touch it or the same key was already there (a multiset difference, so a
    second copy of an old violation is new). Everything else is *introduced* and fails, and
    so is everything when the diff cannot be computed (loud, never a pass). The pre-existing
    count is printed so it can only go down. Every message must carry its `check N: `
    prefix (`tests/test_audit_docs_check_prefixes.py` holds this gate to it).
    """
    total = sum(len(v) for v in found.values())
    if not total:
        notes.append(f"{check}: 0 violation(s) in scope")
        return
    touched = _touched_paths()
    introduced = 0
    for rel, items in sorted(found.items()):
        base_text = _text_at_base(rel) if touched is not None else None
        if base_text is None:
            base_keys: collections.Counter[str] = collections.Counter()
        elif rel not in (touched or set()):
            base_keys = collections.Counter(key for key, _ in items)
        else:
            with tempfile.TemporaryDirectory() as tmp:
                old = pathlib.Path(tmp) / rel
                old.parent.mkdir(parents=True, exist_ok=True)
                old.write_text(base_text, encoding="utf-8")
                base_keys = collections.Counter(at_base(old, tmp))
        for key, message in items:
            if base_keys[key] > 0:
                base_keys[key] -= 1
                continue
            introduced += 1
            if not message.startswith(f"{check}: "):
                raise ValueError(f"{check}: gate message without its prefix: {message!r}")
            fail(message)
    where = f"{_BASE_REF}...HEAD" if touched is not None else f"no diff against {_BASE_REF}"
    notes.append(
        f"{check}: {total - introduced} pre-existing violation(s) in scope (counted, not "
        f"failed; this number can only go down), {introduced} introduced by this change "
        f"({where}) and failed"
    )


def _safe_header(path: pathlib.Path) -> object | None:
    """`_docid.parse_header`, returning `None` instead of raising.

    For the **warn-only** check 38 only: an unparseable header is check 30's failure to
    report, and re-reporting it from a check that cannot fail would be a second voice on one
    defect. Every failing check parses headers directly so the error surfaces where it is
    owned.
    """
    try:
        return _docid.parse_header(path)
    except _docid.HeaderError:
        return None


def _canon_id(raw: str) -> str:
    """`"PL-1240"`, `"PL-01240"` and `"PL-001240"` all resolve to `"PL-1240"` (RFC-937
    §1.1 rule 3) — the same equivalence `_docid.ID_RE`'s `0*` group already encodes;
    this just re-renders whatever matched in canonical (unpadded) form. Returns `raw`
    unchanged when it is not `<PREFIX>-<n>` shaped at all, so a caller can use this on
    arbitrary strings (a `relates:` entry, a `was:` value) without a separate guard.
    """
    m = _docid.ID_RE.fullmatch(raw.strip())
    if m is None:
        return raw
    return _docid.canonical(m.group(1), int(m.group(2)))


# =========================================================================================
# Check 30 — header present and parseable; no unknown field; required fields per family,
# read from docs/_templates/ (RL-981).
# =========================================================================================

_LEADING_COMMENT_RE: Final = re.compile(r"\A<!--.*?-->\n?\n?", re.DOTALL)
_FENCED_YAML_RE: Final = re.compile(r"```yaml\n(.*?)\n```", re.DOTALL)
_TEMPLATE_KEY_RE: Final = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):")

#: RFC-937 §1.2's "Kind" column, keyed by the template's own filename — needed because a
#: template's filename (`FD.md`) is not the family word (`finding`) `Header.family`
#: carries, and `_docid.py` has no filename->family table (only prefix->family, and a
#: template's filename is a family *label*, not a prefix-and-number). `PHASE.md` is
#: deliberately absent: RFC-937 §1.1 rule 4 puts a phase outside the id standard
#: entirely, so it has no family and no header field policy to derive.
_TEMPLATE_FAMILY: Final[Mapping[str, str]] = {
    "ADR.md": "decision",
    "CR.md": "closure",
    "FD.md": "finding",
    "LG.md": "ledger",
    "PL.md": "plan",
    "REFERENCE.md": "reference",
    "RFC.md": "proposal",
    "RL.md": "ruling",
    "RS.md": "research",
    "WF.md": "workflow",
    "WK.md": "work",
    "SL.md": "slice",
}

#: The fields every family's template declares (all thirteen carry `family`, `title`,
#: `status`, `created`, `owner`; twelve of thirteen also carry `id` — Reference is the one
#: family with none, §1.2: "carries no prefix and no number"). Required-ness beyond this
#: core is a per-family template fact, not hand-listed here (RL-981 §2 point 1: "the
#: permitted set for a family is the set of keys in that family's template front matter").
_CORE_HEADER_FIELDS: Final = ("family", "title", "status", "created", "owner")


#: The exact thirteen template filenames RFC-937 §1.2 names, hardcoded rather than
#: inferred from a directory listing — a coverage count taken against `glob("*.md")`'s
#: own result is self-consistent even when a file has silently vanished (it would just
#: report "13 of 13" over a directory that in fact holds 12), which is indistinguishable
#: from correct. Comparing the *listing itself* against this manifest is what a scope
#: change that quietly drops a file cannot pass through unnoticed.
_EXPECTED_TEMPLATE_FILENAMES: Final = frozenset(
    {"ADR.md", "CR.md", "FD.md", "LG.md", "PL.md", "REFERENCE.md", "RFC.md", "RL.md",
     "RS.md", "WF.md", "WK.md", "SL.md", "PHASE.md"}
)
#: Of those thirteen, the ten with a top-level `---` block (every document family).
_EXPECTED_DASH_BLOCK_TEMPLATES: Final = frozenset(
    {"ADR.md", "CR.md", "FD.md", "LG.md", "PL.md", "REFERENCE.md", "RFC.md", "RL.md",
     "RS.md", "WF.md"}
)
#: The two row families, a fenced ```yaml block under the row's own heading (RFC-937
#: §1.5) rather than top-level front matter.
_EXPECTED_FENCED_BLOCK_TEMPLATES: Final = frozenset({"WK.md", "SL.md"})
#: The one family outside the id standard entirely (RFC-937 §1.1 rule 4): no `---`, no
#: fence, no `id:`, no `family:` — checked, not merely assumed, by `derive_field_policies`.
_EXPECTED_NO_BLOCK_TEMPLATES: Final = frozenset({"PHASE.md"})


def _template_front_matter_lines(path: pathlib.Path) -> tuple[list[str] | None, str]:
    """The raw `key: value` lines of one template's declared block, plus which shape
    produced them — `"dash"` (a top-level `---` block), `"fenced"` (a ```yaml block), or
    `"none"` (`PHASE.md`, by design — RFC-937 §1.1 rule 4) — read *after* stripping the
    template's own leading `<!-- ... -->` comment. The shape is returned alongside the
    lines (not just inferred from `None`-ness) so `derive_field_policies` can assert each
    template landed in its *expected* one of the three, not merely "a block or not".

    Deliberately not `_docid.parse_header`: a template's placeholder values
    (`created: YYYY-MM-DD`, `id: PL-NNNNN`) are not valid `Header` content, and are not
    meant to be — this reads a template as a *policy source* (field names only), never as
    a document instance (RL-981 §2 point 3).
    """
    text = path.read_text(encoding="utf-8")
    stripped = _LEADING_COMMENT_RE.sub("", text, count=1)
    lines = stripped.splitlines()
    if lines and lines[0] == "---":
        try:
            closing = lines.index("---", 1)
        except ValueError:
            closing = len(lines)
        return lines[1:closing], "dash"
    fenced = _FENCED_YAML_RE.search(stripped)
    if fenced is not None:
        return fenced.group(1).splitlines(), "fenced"
    return None, "none"


def _template_field_keys(path: pathlib.Path) -> tuple[tuple[str, ...] | None, str]:
    """The set of front-matter keys one family template declares, and its block shape —
    see `_template_front_matter_lines`. The keys are `None` only for the `"none"` shape.
    """
    lines, shape = _template_front_matter_lines(path)
    if lines is None:
        return None, shape
    keys = []
    for line in lines:
        if not line.strip() or line[:1] in (" ", "\t"):
            continue
        m = _TEMPLATE_KEY_RE.match(line)
        if m:
            keys.append(m.group(1))
    return tuple(keys), shape


@dataclass(frozen=True)
class _FieldPolicy:
    """One family's header field policy, derived from its template (RL-981)."""

    permitted: frozenset[str]
    required: frozenset[str]


def derive_field_policies() -> dict[str, _FieldPolicy]:
    """RFC-937 §1.5's per-family header field policy, read from `docs/_templates/` —
    never transcribed from §1.5's own parenthesis (RL-981 §2: "the parenthesis is
    illustration of why extras exist, not the register of which ones do"; measured at
    `f226891` to diverge from the templates in both directions at once).

    Asserts its own coverage against a *hardcoded* manifest rather than inferring it from
    a green caller or from the directory's own listing (RL-981 §4 item 3, sharpened
    2026-09-02): a coverage count taken over `glob("*.md")`'s own result is
    self-consistent even when a file has silently vanished from the thirteen — it would
    report "N of N" over whatever N the directory now holds, which is exactly as
    "defensible-looking" whether N is 13 or 12. Every one of three things is checked
    against `_EXPECTED_TEMPLATE_FILENAMES` and its two named subsets, by name, before any
    policy is derived: the directory holds exactly the thirteen expected filenames and no
    others; the ten expected `_EXPECTED_DASH_BLOCK_TEMPLATES` each produced a `"dash"`
    block; the two expected `_EXPECTED_FENCED_BLOCK_TEMPLATES` each produced a `"fenced"`
    block; `PHASE.md` alone produced `"none"`. This is the specific failure the naive
    shared-parser reader hit first (0 of 13 templates parsed, an empty policy, a pass on
    the very first run) generalised one level: a *partial* regression — one template
    silently losing its block, or one file silently deleted — must be exactly as loud as
    the total one was.
    """
    on_disk_names = {p.name for p in _TEMPLATES_DIR.glob("*.md")}
    if on_disk_names != _EXPECTED_TEMPLATE_FILENAMES:
        missing = _EXPECTED_TEMPLATE_FILENAMES - on_disk_names
        extra = on_disk_names - _EXPECTED_TEMPLATE_FILENAMES
        raise RuntimeError(
            f"{_TEMPLATES_DIR}: expected exactly {sorted(_EXPECTED_TEMPLATE_FILENAMES)} "
            f"but found {sorted(on_disk_names)} — missing {sorted(missing)}, unexpected "
            f"{sorted(extra)} (RL-981 §4 item 3: a silently vanished template must "
            "not read as a smaller, equally-covered set)"
        )

    policies: dict[str, _FieldPolicy] = {}
    dash_seen: set[str] = set()
    fenced_seen: set[str] = set()
    none_seen: set[str] = set()
    for name in sorted(_EXPECTED_TEMPLATE_FILENAMES):
        path = _TEMPLATES_DIR / name
        keys, shape = _template_field_keys(path)
        family = _TEMPLATE_FAMILY.get(name)

        if shape == "dash":
            dash_seen.add(name)
        elif shape == "fenced":
            fenced_seen.add(name)
        else:
            none_seen.add(name)

        if name in _EXPECTED_NO_BLOCK_TEMPLATES:
            if shape != "none" or keys is not None:
                raise RuntimeError(
                    f"{name}: expected no closed-grammar block (RFC-937 §1.1 rule 4) but "
                    f"the template reader found a {shape!r} block — re-check this function"
                )
            continue

        expected_shape = "dash" if name in _EXPECTED_DASH_BLOCK_TEMPLATES else "fenced"
        if shape != expected_shape or keys is None or family is None:
            raise RuntimeError(
                f"{name}: expected a {expected_shape!r} field-policy block but found "
                f"{shape!r} ({keys!r}), or no recognised family — either a real defect "
                "in the template, or _TEMPLATE_FAMILY needs a new entry (RL-981 §4 "
                "item 3: silent empty coverage is exactly the failure this rules out)"
            )
        permitted = frozenset(keys)
        required = frozenset(_CORE_HEADER_FIELDS) & permitted
        if family != "reference":
            required = required | ({"id"} & permitted)
        policies[family] = _FieldPolicy(permitted=permitted, required=required)

    if dash_seen != _EXPECTED_DASH_BLOCK_TEMPLATES:
        raise RuntimeError(
            f"expected exactly {sorted(_EXPECTED_DASH_BLOCK_TEMPLATES)} to carry a "
            f"top-level `---` block; got {sorted(dash_seen)}"
        )
    if fenced_seen != _EXPECTED_FENCED_BLOCK_TEMPLATES:
        raise RuntimeError(
            f"expected exactly {sorted(_EXPECTED_FENCED_BLOCK_TEMPLATES)} to carry a "
            f"fenced ```yaml block; got {sorted(fenced_seen)}"
        )
    if none_seen != _EXPECTED_NO_BLOCK_TEMPLATES:
        raise RuntimeError(
            f"expected exactly {sorted(_EXPECTED_NO_BLOCK_TEMPLATES)} to carry no block "
            f"at all; got {sorted(none_seen)}"
        )
    return policies


#: `Header` fields checked for "populated but not in the family's permitted set" — a
#: field the closed grammar knows globally but this family's *template* never declares.
#: List fields use non-empty as "populated"; `vendored` uses `True` (its `False` default
#: is indistinguishable from absence, which is the common, harmless case here).
#:
#: Deliberately **excludes** `was:`, `vendored:` and `origin:`, verified rather than
#: assumed: `git grep -n '^was:\|^vendored:\|^origin:' docs/_templates/` returns nothing
#: — no template's front-matter block declares any of the three, because all thirteen
#: are freshly-authored examples and these three apply only to a file *after* something
#: has already happened to it (a migration rename for `was:`; being a vendored skill's
#: own `SKILL.md` for `vendored:`/`origin:`, per RFC-937 §1.5's own prose rather than its
#: front-matter illustration). Deriving their permission from "does the template show it"
#: would forbid all three on every family, everywhere, forever — the opposite of what
#: §1.5 states. They stay known (via `_docid.py`'s closed grammar, so a genuine typo in
#: one still lands in `.extra` and is caught) without being template-gated.
_OPTIONAL_HEADER_FIELDS: Final[tuple[str, ...]] = (
    "id", "kind", "phase", "work", "slice", "tree", "plans", "supersedes",
    "superseded_by", "corrected_by", "corrects", "relates",
)


def _is_populated(header: object, field: str) -> bool:
    value = getattr(header, "slice_" if field == "slice" else field)
    if isinstance(value, tuple):
        return len(value) > 0
    if isinstance(value, bool):
        return value is True
    return value is not None


def check_header_fields() -> None:
    """30. Header present and parseable on every file in scope; no unknown field;
    required fields per family (RFC-937 §1.11).

    Renumbered from `check_notes_tombstone`'s retired slot 30 -- see this module's
    docstring for the dated substitution note (RFC-937 §5.5).

    `docs/_templates/` is read for its field policy (`derive_field_policies`), never
    validated as a document instance. `document-ids.md` (S1's one real document in scope)
    is validated as one: parsed under `_docid.parse_header`, checked against its family's
    derived permitted set for an unknown field (`.extra`, plus any globally-known field
    populated where its family's template does not declare it), and checked for every
    field the derived required set names.
    """
    try:
        policies = derive_field_policies()
    except RuntimeError as exc:
        # A clean gate failure, not a crash: letting this propagate as an uncaught
        # exception would abort the whole script before checks 31-39 ever run, trading a
        # readable report for a traceback over the exact condition this assertion exists
        # to make loud in the first place.
        fail(f"check 30: {exc}")
        return
    notes.append(
        f"check 30: field policy derived from all {len(_EXPECTED_TEMPLATE_FILENAMES)} "
        f"templates under {_TEMPLATES_DIR.relative_to(REPO).as_posix()} — "
        f"{len(_EXPECTED_DASH_BLOCK_TEMPLATES)} `---`-block families, "
        f"{len(_EXPECTED_FENCED_BLOCK_TEMPLATES)} fenced-block families, "
        f"{len(_EXPECTED_NO_BLOCK_TEMPLATES)} with no block by design "
        f"({len(policies)} field polic{'y' if len(policies) == 1 else 'ies'} total)"
    )

    # F83's exemption register, consulted here because the scope selector now reaches the
    # files it exists for. `_id_scope_documents` expands a directory root through RFC-937
    # §4 step 5's stamp-set predicate rather than a markdown glob (`F87`), so a widened
    # scope brings in the 59 `.json`, the `.yaml` and the two other non-markdown artifacts
    # the register accounts for — every one of which would otherwise red this check with
    # "no `---` front-matter header found", which is true and is not a defect: a YAML
    # front-matter block prepended to JSON produces a file that no longer parses as JSON.
    # The register is the ruled answer to "why not", and `_check_unstampable_register`
    # holds it to set equality with the files that genuinely cannot be stamped, so this
    # skip cannot be widened by adding a row without that reconciliation failing.
    found: dict[str, list[tuple[str, str]]] = {}
    for path in _governed_documents():
        rel = path.relative_to(REPO).as_posix()
        msgs = _header_problems(path, rel, policies)
        if msgs:
            found[rel] = [(m, m) for m in msgs]
    _residue_gate(
        "check 30",
        found,
        lambda old, tmp: _header_problems(old, old.relative_to(tmp).as_posix(), policies),
    )


def _header_problems(
    path: pathlib.Path, rel: str, policies: Mapping[str, _FieldPolicy]
) -> list[str]:
    """Every check-30 problem in one governed document (empty when it passes)."""
    try:
        header = _docid.parse_header(path)
    except _docid.HeaderError as exc:
        return [f"check 30: {rel}: {exc}"]
    if header is None:
        return [f"check 30: {rel}: no `---` front-matter header found"]
    out: list[str] = []
    policy = policies.get(header.family)
    if policy is None:
        return [
            f"check 30: {rel}: family {header.family!r} has no known template under "
            f"{_TEMPLATES_DIR.relative_to(REPO).as_posix()}"
        ]
    for extra_key in header.extra:
        if extra_key in policy.permitted:
            continue
        out.append(
            f"check 30: {rel}: unknown field `{extra_key}:` — not in family "
            f"{header.family!r}'s permitted set (docs/_templates/ does not declare "
            "it for this family; RL-1140 DP-8.1: an extra is licensed per family, "
            "never globally)"
        )
    for field in _OPTIONAL_HEADER_FIELDS:
        if field in policy.permitted:
            continue
        if _is_populated(header, field):
            out.append(
                f"check 30: {rel}: field `{field}:` is populated but not permitted "
                f"for family {header.family!r} (docs/_templates/ does not declare it)"
            )
    for required_field in sorted(policy.required):
        if required_field == "id":
            present = header.id is not None
        elif required_field == "created":
            present = header.created is not None
        else:
            present = bool(getattr(header, required_field))
        if not present:
            out.append(
                f"check 30: {rel}: missing required field `{required_field}:` for "
                f"family {header.family!r}"
            )
    return out


# =========================================================================================
# Check 31 — id/filename/directory agreement; numbers unique and contiguous in scope;
# `created` non-decreasing with the number. `_templates/` is exempt by path (RFC-937 §1.4).
# =========================================================================================

#: RFC-937 §1.4's directory-is-the-family table, prefix -> directory, document families
#: only (row families FR/NFR/DEP/OQ/WK/SL live embedded in a shared file, not their own
#: directory). A second, independent transcription of the same note table —
#: `scripts/doc-index.py`'s own `FAMILY_DIRS` transcribes it for that module's purpose —
#: is the intended shape (one shared low-level parser, `_docid.py`, with each higher-level
#: consumer reading its own small, static projection of a table that changes only via an
#: RFC-/RL- per RFC-937 §1.12), not the drift RFC-756 warns against.
_FAMILY_DIR: Final[Mapping[str, str]] = {
    "WF": "workflows", "ADR": "adrs", "RFC": "rfcs", "PL": "plans", "LG": "ledgers",
    "RL": "rulings", "RS": "research", "CR": "closures", "FD": "findings",
}

_FILENAME_ID_RE: Final = re.compile(
    rf"^({'|'.join(_docid.FAMILY_PREFIXES)})-(\d+)-"
)


def check_id_filename_directory() -> None:
    """31. Header `id` prefix and integer equal the filename's; directory equals family;
    numbers unique and contiguous in scope; `created` non-decreasing with the number
    (RFC-937 §1.11).

    On the real tree in S1 this has exactly one candidate (`document-ids.md`), which
    carries no `id:` at all (Reference, §1.2: "no prefix and no number") — so every
    sub-clause finds nothing to compare *today*; each is proven on fixtures instead.

    Contiguity (RL-1061) reads the full allocation via docs/INDEX.md (same as row (b)
    in `doc-id.py check`) rather than per-file, to avoid false gaps between document
    families in the scoped walk. Other clauses remain per-file, run over the scoped
    working tree as part of `audit-docs.py`'s single report (RFC-937 §1.11: "one gate,
    one report").
    """
    entries: list[tuple[int, str, str, date | None]] = []
    for path in _id_scope_documents():
        rel = path.relative_to(REPO).as_posix()
        try:
            header = _docid.parse_header(path)
        except _docid.HeaderError:
            continue  # check 30 already reports a malformed header
        if header is None or header.id is None:
            continue
        m = _docid.ID_RE.fullmatch(header.id.strip())
        if m is None:
            fail(f"check 31: {rel}: header `id: {header.id}` is not `<PREFIX>-<n>` shaped")
            continue
        prefix, number = m.group(1), int(m.group(2))

        filename_m = _FILENAME_ID_RE.match(path.name)
        if filename_m is not None:
            f_prefix, f_number = filename_m.group(1), int(filename_m.group(2))
            if (prefix, number) != (f_prefix, f_number):
                fail(
                    f"check 31: {rel}: header id {_docid.canonical(prefix, number)} but "
                    f"filename pads {_docid.canonical(f_prefix, f_number)}"
                )

        expected_dir = _FAMILY_DIR.get(prefix)
        if expected_dir is not None and path.parent.name != expected_dir:
            fail(
                f"check 31: {rel}: family {header.family!r} (prefix {prefix}) belongs "
                f"under a {expected_dir!r} directory, not {path.parent.name!r}"
            )

        entries.append((number, _docid.canonical(prefix, number), rel, header.created))

    seen: dict[int, tuple[str, str]] = {}
    for number, canon, rel, _created in entries:
        earlier = seen.get(number)
        if earlier is not None:
            fail(
                f"check 31: {number} is claimed by both {earlier[0]} ({earlier[1]}) and "
                f"{canon} ({rel})"
            )
        else:
            seen[number] = (canon, rel)

    # ADR 8449 (ND-3): uniqueness of the one id sequence is what is guarded; contiguity
    # over docs/INDEX.md is dropped, because INDEX is frozen and a new id never enters it.
    scoped_count = len(seen)

    dated = sorted((n, c) for n, _canon, _rel, c in entries if c is not None)
    for (n1, c1), (n2, c2) in itertools.pairwise(dated):
        if n1 != n2 and c2 < c1:
            fail(
                f"check 31: id {n2} is `created:` {c2.isoformat()}, earlier than id "
                f"{n1}'s {c1.isoformat()} — `created` must be non-decreasing with the number"
            )

    notes.append(f"check 31: {len(entries)} id(s) in scope, {scoped_count} distinct number(s)")


# =========================================================================================
# Check 32 — citation resolution and padding hygiene. Gated on docs/INDEX.md existing.
# =========================================================================================

_MD_LINK_RE: Final = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
_FENCE_LINE_RE: Final = re.compile(r"^\s*```")

def citation_problems_in_file(path: pathlib.Path, index_ids: set[str]) -> list[str]:
    """Every check-32 problem in one file, given the set of canonical ids `docs/INDEX.md`
    carries: a `<PREFIX>-<n>` citation outside a link target that does not resolve; the
    same citation written padded; a markdown link whose text and target cite different
    ids. Explicit parameters (not the module's own `ROOT`/`_id_scope_documents`) so a
    fixture can exercise this without a real `docs/INDEX.md` on disk.

    `docs/rulings/RL-01060-check-36-is-one-rule-at-two-times-with-d-and-must-carry-d-s-disclosed-classes-check-32-s-padding-resolution-clause-adopts-e-s-conjuncts-from-docid-not-a-private-re-typing.md`
    Entry 2 item
    1: the padding clause adopts row (e)'s conjuncts 1, 2 and 3 from `_docid` — the
    exact-width regex (conjunct 1, `_docid._PADDED_ID_RE`, read here rather than
    reassembled from its own `FAMILY_PREFIXES`/`PAD_WIDTH` symbols a second time), path
    exclusion (conjunct 2, `_docid._in_path_context`) and resolution (conjunct 3: a padded
    token whose unpadded form does not resolve in `docs/INDEX.md` is a specimen of the
    form, not a citation, exactly as (e) reads it) — so path-shaped citations and
    unresolvable ids are excluded from the padding population. Check 32 keeps its own
    broader `0*` breadth beyond that (RFC-937 §1.1 rule 2 admits no exception): a padded
    citation outside (e)'s exact-width conjunct is a **short-padded** violation, listed
    under its own text rather than folded into (e)'s count.
    """
    problems: list[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    in_fence = False
    for lineno, line in enumerate(lines, 1):
        if _FENCE_LINE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        link_spans = [m.span() for m in _MD_LINK_RE.finditer(line)]

        # Conjunct 2 path stripping: strip markdown emphasis before path detection
        cleaned = _docid._MD_EMPHASIS_RE.sub("", line)

        for m in _docid.ID_RE.finditer(line):
            if any(start <= m.start() < end for start, end in link_spans):
                continue  # a link target may legitimately carry a padded id
            prefix, number_s = m.group(1), m.group(2)
            canon = _docid.canonical(prefix, int(number_s))
            if canon not in index_ids:
                problems.append(f"{lineno}: {canon} does not resolve in docs/INDEX.md")
            # `_docid.ID_RE`'s own `0*` sits *outside* the number group, so it strips a
            # padded citation's leading zero before `m.group(2)` ever sees it — comparing
            # the two capture groups can never find padding. The full match (`m.group(0)`)
            # still carries it, so that is what padding is detected against.
            if m.group(0) != canon:
                # Conjunct 3 — an unresolvable padded id is a specimen of the form, not a
                # citation this rule ever governed; the "does not resolve" problem above
                # already reports it, so it contributes nothing further here.
                if canon not in index_ids:
                    continue
                # Conjunct 2 — exclude padded ids in path contexts. Map position from the
                # original line to the cleaned line (emphasis removed).
                cleaned_start = len(_docid._MD_EMPHASIS_RE.sub("", line[:m.start()]))
                cleaned_end = cleaned_start + len(
                    _docid._MD_EMPHASIS_RE.sub("", m.group(0))
                )
                if _docid._in_path_context(cleaned, cleaned_start, cleaned_end):
                    continue
                if _docid._PADDED_ID_RE.fullmatch(m.group(0)):
                    problems.append(
                        f"{lineno}: padded id `{m.group(0)}` outside a link target — "
                        "citations write the integer, never padding (RFC-937 §1.1 rule 2)"
                    )
                else:
                    problems.append(
                        f"{lineno}: short-padded id `{m.group(0)}` outside a link "
                        "target — fewer leading zeros than `_docid.PAD_WIDTH`, still a "
                        "rule-2 violation row (e)'s exact-width conjunct does not see "
                        "(RFC-937 §1.1 rule 2)"
                    )

        for link_m in _MD_LINK_RE.finditer(line):
            text, target = link_m.group(1), link_m.group(2)
            text_m = _docid.ID_RE.search(text)
            target_m = _docid.ID_RE.search(target)
            if text_m and target_m:
                text_id = _docid.canonical(text_m.group(1), int(text_m.group(2)))
                target_id = _docid.canonical(target_m.group(1), int(target_m.group(2)))
                if text_id != target_id:
                    problems.append(
                        f"{lineno}: link text {text!r} cites {text_id} but its target "
                        f"{target!r} names {target_id}"
                    )
    return problems


def _header_ids() -> set[str]:
    """Canonical ids carried by the front matter of every governed document in scope."""
    found: set[str] = set()
    for path in _id_scope_documents():
        try:
            header = _docid.parse_header(path)
        except _docid.HeaderError:
            continue  # check 30 already reports a malformed header
        if header is None or header.id is None:
            continue
        m = _docid.ID_RE.fullmatch(header.id.strip())
        if m is not None:
            found.add(_docid.canonical(m.group(1), int(m.group(2))))
    return found


_LINENO_RE: Final = re.compile(r":\d+:")  # a line number moves when text above it is edited


def check_citations() -> None:
    """32. Every `<PREFIX>-<n>` in prose resolves in `docs/INDEX.md` and its prefix
    matches the number's family (the prefix is a checksum — `_docid.ID_RE` already
    requires this by construction, since a resolved match is keyed on the number alone
    and its recorded prefix compared); no padded id outside a link target; a link's text
    and target cite the same id (RFC-937 §1.11).

    Gated on `docs/INDEX.md` existing: pre-migration there is no real citation corpus to
    resolve against, and `document-ids.md`'s own illustrative prose (the padding-
    equivalence example in its lift of RFC-937 §1.1 rule 3 — "the resolver treats
    `PL-1240`, `PL-01240` and `PL-001240` as one id" — and the §1.4 directory-tree
    diagram) uses ids, some deliberately padded, to *teach* the grammar rather than to
    cite or name a real file. Running the padding rule against that prose unconditionally
    would red the standard's own reference text for demonstrating the equivalence it
    defines. Every sub-rule activates together once `docs/INDEX.md` exists (W37-6); the
    mechanism (`citation_problems_in_file`) is proven on fixtures in the interim.
    """
    index_path = ROOT / "INDEX.md"
    if not index_path.is_file():
        # "0 document(s) examined" stated explicitly, not just "skipped": a check that
        # examines zero documents and passes must say so in a way that is loud on its
        # own, not only true on a close reading — the same principle F76's guard serves
        # one call up the stack.
        notes.append(
            "check 32: 0 document(s) examined — no docs/INDEX.md yet, citation and "
            "padding checks skipped (pre-migration; document-ids.md's own illustrative "
            "ids would otherwise false-positive)"
        )
        return
    # ADR 8449 (ND-4): a frozen-family id resolves against the frozen INDEX; an id minted
    # after the freeze never enters INDEX, so it resolves against the governed headers.
    index_ids = {
        _docid.canonical(m.group(1), int(m.group(2)))
        for m in _docid.ID_RE.finditer(index_path.read_text(encoding="utf-8"))
    } | _header_ids()
    checked = 0
    found: dict[str, list[tuple[str, str]]] = {}
    for path in _id_scope_documents():
        rel = path.relative_to(REPO).as_posix()
        # F103, 2026-09-17: the generated-contract tier
        # (`_docid.generated_contract_tier_reason`) is written by `generate-contracts.py`
        # from the models, never a citation a person wrote — `_id_scope_documents()`
        # still reaches it for check 30's F83 exemption bookkeeping, but check 32's
        # citation-resolution rule reads the identical narrow shared predicate the
        # migration's own (d)/(e) corpus already excludes it by, rather than scanning a
        # tier this check was never meant to police. The narrow predicate, not the full
        # `_docid.sweep_exclusion_reason` — that also folds in `FIXTURE_CORPUS_ROOTS`,
        # which reaches files check 32 has no reason to exempt.
        #
        # W37-6 h1-check36 follow-up, 2026-09-17: the governance-record class
        # (`_docid.governance_record_reason`) — a record such as
        # `docs/research/file-census-<sha>.csv` that quotes legacy paths/tokens as
        # evidence of the residue they name, never a citation for the migration to
        # rewrite — is excluded from the migration sweep by the identical shared
        # predicate and must be invisible to check 32 for the same reason the
        # generated-contract tier is: reading its data cells as citations produces
        # unresolvable-id failures for text the record is not citing.
        if (
            _docid.generated_contract_tier_reason(rel) is not None
            or _docid.governance_record_reason(rel) is not None
        ):
            continue
        problems = [
            f"check 32: {rel}:{problem}" for problem in citation_problems_in_file(path, index_ids)
        ]
        if problems:
            found[rel] = [(_LINENO_RE.sub(":", m, count=1), m) for m in problems]
        checked += 1
    # ADR 8449: a citation that does not resolve and was already there (the one in a skill's
    # prose) is counted, never rewritten away; one this change introduces fails.
    _residue_gate(
        "check 32",
        found,
        lambda old, tmp: [
            _LINENO_RE.sub(":", f"check 32: {old.relative_to(tmp).as_posix()}:{problem}", count=1)
            for problem in citation_problems_in_file(old, index_ids)
        ],
    )
    notes.append(f"check 32: {checked} file(s) checked against {len(index_ids)} indexed id(s)")


# =========================================================================================
# Check 33 — supersedes/superseded_by symmetry; status vocabulary and per-family subset;
# the map-plan roll-up raise (RL-983).
# =========================================================================================

#: RFC-937 §1.2's Status subset column, prefix (or family word for Reference, which has
#: no prefix) -> the allowed subset of `_docid.STATUS_WORDS`.
_STATUS_SUBSET: Final[Mapping[str, frozenset[str]]] = {
    "FR": frozenset({"active", "superseded", "retired"}),
    "NFR": frozenset({"active", "superseded", "retired"}),
    "DEP": frozenset({"active", "superseded", "retired"}),
    "OQ": frozenset({"active", "closed", "retired"}),
    "WK": frozenset({"draft", "active", "closed", "retired"}),
    "SL": frozenset({"draft", "active", "closed", "retired"}),
    "WF": frozenset({"draft", "active", "superseded", "retired"}),
    "ADR": frozenset({"draft", "active", "superseded", "retired"}),
    "RFC": frozenset({"draft", "active", "closed", "retired", "superseded"}),
    "PL": frozenset({"draft", "active", "superseded", "retired"}),
    "LG": frozenset({"active", "closed"}),
    "RL": frozenset({"active", "superseded", "retired"}),
    "RS": frozenset({"draft", "active", "closed", "retired"}),
    "CR": frozenset({"active"}),
    "FD": frozenset({"active", "closed", "retired"}),
    "reference": frozenset({"active", "retired"}),
}


def rollup_raise_problems(corpus: object) -> list[str]:
    """For every `PL- kind: map` header `corpus` carries, call `doc-index.py`'s own
    `derive_execution` and report a `ValueError` as a check-33 problem. RL-983's own
    words: "a slice with more than one live leaf plan is a check 33 disagreement, not a
    case to resolve silently", and the precedence table's own last row ("anything else:
    raise") is what makes an unenumerated combination visible instead of swallowed by a
    default. Takes an already-built `doc_index.Corpus` (untyped here as `object` since
    that class lives in a dynamically loaded module) rather than a root path, so it is the
    exact function both this check and its tests call.
    """
    problems: list[str] = []
    for header in corpus.headers():  # type: ignore[attr-defined]
        if header.family != "plan" or header.kind != "map":
            continue
        try:
            _doc_index.derive_execution(header, corpus)
        except ValueError as exc:
            problems.append(f"{header.id}: map-plan roll-up disagreement — {exc}")
    return problems


def check_cross_references() -> None:
    """33. `supersedes`/`superseded_by` symmetric; `status:` is in RFC-937's five-word
    vocabulary and in the family's own subset of it; the map-plan roll-up raise surfaced
    rather than swallowed (RL-983) (RFC-937 §1.11).

    Several §1.11 sub-clauses (a ledger's `slice:` uniqueness across `active` ledgers,
    `work:`/`slice:`/`phase:` resolving to roadmap rows, a closed `OQ-` citing its
    resolver) need a corpus with roadmap/ledger/OQ content that does not exist inside
    `_ID_SCOPE_ROOTS` in S1 — `document-ids.md` is the only real document in scope, and it
    is none of those things; they are not implemented against the live scope for that
    reason. The roll-up raise is likewise never exercised against the live scope here (no
    `PL-` corpus can exist inside two flat roots, and `doc_index.build_corpus` needs a
    `docs/`-shaped tree of `plans/`, `roadmap.md`, etc. to find one) — `rollup_raise_problems`
    above is written to take an explicit corpus precisely so it is proven on a fixture
    corpus in `tests/test_audit_docs_ids.py` without widening this check's own scope.
    """
    headers: dict[str, _docid.Header] = {}
    parsed: list[tuple[pathlib.Path, _docid.Header]] = []
    for path in _id_scope_documents():
        try:
            header = _docid.parse_header(path)
        except _docid.HeaderError:
            continue
        if header is None:
            continue
        parsed.append((path, header))
        if header.id is not None:
            headers[_canon_id(header.id)] = header

    checked = 0
    for path, header in parsed:
        rel = path.relative_to(REPO).as_posix()
        checked += 1

        if header.status and header.status not in _docid.STATUS_WORDS:
            fail(
                f"check 33: {rel}: status {header.status!r} is not one of "
                f"{_docid.STATUS_WORDS}"
            )
        else:
            status_key = header.id.split("-")[0] if header.id else header.family
            subset = _STATUS_SUBSET.get(status_key) or _STATUS_SUBSET.get(header.family)
            if subset is not None and header.status and header.status not in subset:
                fail(
                    f"check 33: {rel}: status {header.status!r} is not in "
                    f"{header.family}'s subset {sorted(subset)}"
                )

        if header.status == "superseded":
            if not header.superseded_by:
                fail(f"check 33: {rel}: status superseded but superseded_by is empty")
            else:
                target = headers.get(_canon_id(header.superseded_by))
                if target is not None and header.id is not None:
                    back_refs = {_canon_id(s) for s in target.supersedes}
                    if _canon_id(header.id) not in back_refs:
                        fail(
                            f"check 33: {rel}: superseded_by {header.superseded_by} does "
                            f"not list {header.id} back in its own supersedes:"
                        )

    notes.append(f"check 33: {checked} header(s) checked in scope")


# =========================================================================================
# Check 34 — freeze (DP-7): a frozen family's diff against its merge-base touches only the
# allowed fields; every corrected_by: entry's target corrects: this file.
# =========================================================================================

#: Mutability = "frozen" families, from RFC-937 §1.2's table. Document families only; row
#: families have no separate freeze concept (check 33's status-forward-only and
#: closed-LG-required rules constrain an `SL-` row's lifecycle instead).
_FROZEN_FAMILIES: Final = frozenset(
    {"decision", "proposal", "plan", "ruling", "research", "closure", "finding"}
)
_LEDGER_FAMILY: Final = "ledger"

#: Every `Header` field DP-7 does *not* name as an allowed change on a frozen file. Built
#: by exclusion from the dataclass's own field list so a future field added to `Header`
#: fails loudly here (an unrecognised field name) rather than silently becoming a fifth
#: allowance nobody decided on.
_DP7_UNCHECKED_FIELDS: Final = frozenset({"status", "superseded_by", "plans", "corrected_by"})


def frozen_diff_is_permitted(
    old: object, new: object, *, old_body: str, new_body: str
) -> tuple[bool, str]:
    """DP-7 (docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md): every diff a frozen
    (or append-only, for a ledger's `plans:`) family's file may show against its
    merge-base — a closed, named list of *fields*, never a generic line-diff. Exported at
    module level, not nested inside `check_freeze`, so a later slice's migration-diff
    filter can call the exact same predicate for its own "hunk is neither header nor
    citation-token" test (RL-989 — DP-3: "one definition of 'reference tokens only',
    not two ... implementing it twice is how the two drift apart").

    `old`/`new` are `_docid.Header` instances (typed `object` here only because this
    function must stay independent of which `_docid` module instance a caller loaded
    them through). Permitted, and only:
      - the body (everything after the closing `---`) is byte-identical;
      - `status:` may change, but never *from* a terminal word (`closed`, `retired`,
        `superseded` — RFC-937 §1.2a: "closed, retired and superseded are terminal");
      - `superseded_by:` may change;
      - `corrected_by:` may gain entries, never lose or reorder existing ones;
      - `plans:` may gain entries, ledgers only, under the same append-only rule.
    Every other field difference refuses. This is the *steady-state* freeze rule, deliberately
    narrower than what the migration itself does to a frozen file (stamp a header, rewrite
    reference tokens) — that allowance is `frozen_file_matches_after_migration_stamp` below.
    """
    if old_body != new_body:
        return False, "the body changed — a frozen file's body never changes"

    terminal = {"closed", "retired", "superseded"}
    if old.status != new.status and old.status in terminal:  # type: ignore[attr-defined]
        return False, f"status: moved away from terminal state {old.status!r}"  # type: ignore[attr-defined]

    old_corrected = tuple(old.corrected_by)  # type: ignore[attr-defined]
    new_corrected = tuple(new.corrected_by)  # type: ignore[attr-defined]
    if new_corrected[: len(old_corrected)] != old_corrected:
        return False, "corrected_by: entries were removed or reordered, not just appended"

    old_plans = tuple(old.plans)  # type: ignore[attr-defined]
    new_plans = tuple(new.plans)  # type: ignore[attr-defined]
    if old_plans != new_plans:
        if old.family != _LEDGER_FAMILY:  # type: ignore[attr-defined]
            return False, "plans: changed on a non-ledger family"
        if new_plans[: len(old_plans)] != old_plans:
            return False, "plans: entries were removed or reordered, not just appended"

    for field_name in _docid.Header.__dataclass_fields__:  # type: ignore[attr-defined]
        if field_name in _DP7_UNCHECKED_FIELDS:
            continue
        if getattr(old, field_name) != getattr(new, field_name):
            return False, f"{field_name}: changed, which is not on DP-7's allowed list"

    return True, ""


@functools.lru_cache(maxsize=8)
def _inverse_token_pattern(tokens: tuple[str, ...]) -> re.Pattern[str]:
    r"""One alternation over every new token, longest first, matching whole identifiers only.

    Longest-first is the ordering the caller's own docstring already required, and putting
    it inside a single alternation keeps it while making the substitution one pass instead
    of one per token: this predicate runs over every file in the tree against a real
    `REDIRECTS.csv` of ~1 100 entries, and a per-token `re.sub` is roughly two orders of
    magnitude slower than the `str.replace` loop it replaces (measured: the whole-corpus
    §7 (g) run did not finish in 20 minutes, against ~30 s for one pass). Cached because
    the token set is the same for every file of a run.

    The left-hand anchor is `_docid.TOKEN_LEFT_BOUND`, not `\b` -- the deputy's ruling,
    W37-6, 2026-09-04: a plain `\b` inverts a workstream/slice id (`W37-6`) found
    *inside* a longer identifier that merely ends the same way (`F-W37-6`), because `-`
    is itself \W and this grammar uses it as an internal field separator, not a genuine
    word boundary. `doc-id.py`'s `_whole_token_re` carries the full reasoning and proof;
    this is the identical constant on the inverse side of the same mechanism.
    """
    alternation = "|".join(re.escape(tok) for tok in tokens)
    return re.compile(rf"{_docid.TOKEN_LEFT_BOUND}(?:{alternation})\b(?![-/][0-9])")


def _this_runs_stamp_id(
    text: str,
    allocated_ids: Collection[str],
    *,
    rel: str | None = None,
    reference_stamp_paths: Collection[str] = frozenset(),
) -> str | None:
    """`text`'s leading `---`-delimited block's `id:`, but only when that block is a
    header *this run's own migration* wrote — else `None`, meaning "not this run's
    stamp, do not strip it." Returns `""` (not `None`) for a confirmed Reference-family
    stamp, which by design carries no `id:` line at all — see below.

    RL-1046 §2 ("DP-7 must strip only the header this run wrote"): a bare `---`
    opener is not enough, because most of `.claude/skills/**` and `.claude/agents/`
    carry their own, unrelated front matter that also opens with `---` — vendored skill
    or agent config this migration deliberately defers rather than stamping
    (`doc-id.py`'s `_front_matter_state` == `"foreign"`, `"must be merged, not
    prepended"`). `_docid.parse_header_text` even *succeeds* on most of those blocks
    (their `name:`/`description:` keys land in `.extra` with no error) — so a bare
    "did it parse" test is not the filter either, and `id` alone would be `None` for
    virtually every one of them without a second check. `allocated_ids` is the actual
    filter: this run's own `REDIRECTS.csv` `new_id` column, so a header this run did not
    itself just write is left alone even when it happens to parse.

    **`allocated_ids` alone is not sufficient — the Reference family has no `id:` at
    all** (RFC-937 §1.2, `doc-id.py`'s `_stamp_header("REFERENCE", None, ...)`), so its
    stamp can never appear in `allocated_ids` regardless of whether this run wrote it.
    Found live: `.claude/roles/example-role.md` — headerless before this run,
    Reference-stamped by it (`_stamp_reference_targets`, RFC-937 §4 step 5) — read as
    "not this run's stamp" under the `allocated_ids`-only check, so its citation rewrite
    could never reproduce the merge-base bytes and it fell through to
    `classified-by-none` for a rewrite that was entirely correct. `reference_stamp_paths`
    is the caller's set of paths this run's own migration Reference-stamps (`doc-id.py`'s
    `_discover_reference_stamp_targets`, run over the pre-migration tree) — the same
    per-family membership test `allocated_ids` already is for every id-bearing family,
    read from the one place a headerless stamp's provenance can still be checked: which
    paths this run's own stamp writer actually targets, not what its header contains.
    """
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return None
    try:
        header = _docid.parse_header_text(text)
    except _docid.HeaderError:
        return None  # not RFC-937-shaped at all -- e.g. the 3 vendored SKILL.md blocks
    if header is None:
        return None
    if header.id is not None:
        return header.id if header.id in allocated_ids else None
    if rel is not None and rel in reference_stamp_paths:
        return ""  # confirmed: a Reference-family stamp, which carries no id by design
    return None


def stripped_stamp_pair(
    old_body: str,
    new_text: str,
    *,
    allocated_ids: Collection[str] = frozenset(),
    old_rel: str | None = None,
    new_rel: str | None = None,
    reference_stamp_paths: Collection[str] = frozenset(),
) -> tuple[str, str]:
    """`(old_body, new_text)`, each with its own leading front-matter block removed only
    when `_this_runs_stamp_id` confirms it is a stamp *this run's own migration* wrote
    (RL-1046 §2) — extracted from `frozen_file_matches_after_migration_stamp` so a
    second predicate needing the identical stripped pair (`doc-id.py`'s row (g) g2
    forward-citation check, below) shares this one determination of which side's block is
    safe to strip, rather than reimplementing it a second time (RL-989 §3: "one
    definition ... implementing it twice is how the two drift apart").
    """

    def _strip(text: str, rel: str | None) -> str:
        if _this_runs_stamp_id(
            text, allocated_ids, rel=rel, reference_stamp_paths=reference_stamp_paths
        ) is None:
            return text
        lines = text.splitlines()
        closing = lines.index("---", 1)  # present: _this_runs_stamp_id already found it
        return "\n".join(lines[closing + 1 :])

    return _strip(old_body, old_rel), _strip(new_text, new_rel)


def frozen_file_matches_after_migration_stamp(
    old_body: str,
    new_text: str,
    redirects_inverse: Mapping[str, str],
    *,
    allocated_ids: Collection[str] = frozenset(),
    old_rel: str | None = None,
    new_rel: str | None = None,
    reference_stamp_paths: Collection[str] = frozenset(),
) -> bool:
    """RL-989's DP-7 disposition, verbatim: "the new bytes, after removing the leading
    front-matter block and applying the inverse of every REDIRECTS.csv mapping, are
    byte-identical to the merge-base bytes." `redirects_inverse` maps a *new* reference
    token to the *old* one it replaced; applying every entry to `new_text` and stripping
    its own leading `---` block should reproduce `old_body` when the only changes are the
    migration's own header stamp and token rewrite.

    **RL-1046 §2: strip only the header this run wrote, on both sides.** The block
    removed from `new_text` (and, symmetrically, from `old_body` — a frozen-family file
    being updated in place already carries a header from an *earlier* run, and that
    header is not this run's stamp either) is stripped only when `_this_runs_stamp_id`
    confirms it is one this run's own migration produced — its `id:` is in
    `allocated_ids`, this run's own `REDIRECTS.csv` `new_id` column. `allocated_ids`
    defaults to empty, matching the pre-Ruling-105 behaviour of never stripping when a
    caller does not (yet) pass one — a caller wanting the old unconditional strip back
    would have to pass every id it could ever see, which is the point: the default is
    the conservative, no-op side of the change, not a silent revival of the bug.
    Previously this stripped *any* leading `---...---` block unconditionally, which
    besides the vendored-front-matter case above also meant `old_body` (when it is the
    raw pre-migration text, not a header-converted note/ADR body) was compared against a
    `new_text` that had lost content `old_body` still carried — a clean, correct
    citation-token rewrite in a `.claude/skills/**` or `.claude/agents/` file then failed
    this predicate for reasons unrelated to whether the rewrite itself was correct
    (RL-1046 §2, up to 237 of row (g)'s ~504 `classified-by-none` files).

    **`old_rel`/`new_rel`/`reference_stamp_paths`: the Reference family carries no
    `id:` at all**, so `allocated_ids` alone cannot confirm a Reference stamp is this
    run's own (`.claude/roles/example-role.md`, headerless before this run and
    Reference-stamped by it — `_this_runs_stamp_id`'s own docstring has the found-live
    case). All three default to `None`/empty, the same conservative no-op default
    `allocated_ids` already uses: a caller that does not pass them gets exactly the
    id-only behaviour, never a silent new strip.

    Longest `new_token` first (found by W37-5, applying this function against a real
    multi-id redirects map rather than the single-entry maps this module's own tests use):
    RFC-937's citation rule is the bare integer, so two live ids can be in a literal
    prefix relationship — `WK-1` and `WK-17` both exist in most real corpora — and
    replacing the shorter one first corrupts the longer one's own digits (`WK-17` loses
    its `WK-1` prefix to the first substitution before its own entry is ever reached, and
    the now-absent `WK-17` substring makes that second entry a no-op). Processing longest
    to shortest guarantees every occurrence of a longer token is fully substituted, and
    thus absent from the text, before a token it could contain as a prefix is ever tried —
    the identical ordering `scripts/doc-id.py`'s own citation-rewrite pass uses for the
    forward direction, for the identical reason.

    **Whole identifiers only, in this direction too** — RL-1043 §2 row (g)
    (`docs/rulings/RL-01043-no-further-delegated-window-until-7-a-i-is-an-instrument.md`). A plain
    substring inverse has no notion of where an identifier ends, so it *repaired* the very defect §7
    (g) exists to find: given the mangled `NFR-775/14` it substituted `NFR-775` and produced
    `NFR-502/501`, the merge-base bytes exactly, and the file passed. That is the trap the ruling
    names — the mangled citations "must not be treated as a citation-token class and thereby excused
    from §7 (g)'s 'neither header nor citation-token' requirement" — and it was literal: §7 (g)'s
    figure could have been computed on the migrated tree and still read empty. The inverse now
    applies the same rule `_whole_token_re` applies forward, so a token substituted inside a longer
    identifier fails to invert and its file is reported. `\b` alone would not do it: it matches
    between `775` and `/`. The `-`/`/`-followed-by-a-digit form is what the corpus holds; a
    separator followed by a letter (`OQ-500-shaped`) is not a continuation and still inverts.
    """

    old_stripped, stripped = stripped_stamp_pair(
        old_body, new_text, allocated_ids=allocated_ids, old_rel=old_rel, new_rel=new_rel,
        reference_stamp_paths=reference_stamp_paths,
    )
    if not redirects_inverse:
        return stripped.strip("\n") == old_stripped.strip("\n")
    pattern = _inverse_token_pattern(tuple(sorted(redirects_inverse, key=len, reverse=True)))
    restored = pattern.sub(lambda m: redirects_inverse[m.group(0)], stripped)
    return restored.strip("\n") == old_stripped.strip("\n")


def check_freeze() -> None:
    """34. Freeze: for a frozen family the diff against the merge-base touches only the
    DP-7 allowance; every `corrected_by:` entry is a record whose `corrects:` names this
    file (RFC-937 §1.11).

    No in-scope file is ever a frozen-family instance during S1 (`document-ids.md` is a
    Reference, and `_templates/` is excluded as a policy source, not a document), so the
    merge-base comparison — `frozen_diff_is_permitted` above — finds nothing to run
    against on the real tree today; it is exercised directly against constructed old/new
    `Header` pairs in `tests/test_audit_docs_ids.py`. The `corrected_by:`/`corrects:`
    cross-check below *is* live over whatever is in scope.
    """
    headers: dict[str, _docid.Header] = {}
    parsed: list[tuple[pathlib.Path, _docid.Header]] = []
    for path in _id_scope_documents():
        try:
            header = _docid.parse_header(path)
        except _docid.HeaderError:
            continue
        if header is None:
            continue
        parsed.append((path, header))
        if header.id is not None:
            headers[_canon_id(header.id)] = header

    frozen_checked = 0
    for path, header in parsed:
        if header.family not in _FROZEN_FAMILIES:
            continue
        frozen_checked += 1
        for entry in header.corrected_by:
            target = headers.get(_canon_id(entry))
            if target is None:
                continue  # out of scope to resolve in S1 — not a check-34 failure here
            if header.id is not None and _canon_id(target.corrects or "") != _canon_id(header.id):
                fail(
                    f"check 34: {path.relative_to(REPO).as_posix()}: corrected_by entry "
                    f"{entry} does not `corrects:` back to {header.id}"
                )

    notes.append(f"check 34: {frozen_checked} frozen-family file(s) in scope")


# =========================================================================================
# Check 35 — owner: is a role filename or `maintainer`, and one the directory's README.md
# permits (where that README declares a permitted-owner list); and F83's register of
# files that cannot carry a header at all, reconciled against the tree by name.
# =========================================================================================

_ROLES_DIR: Final = REPO / ".claude" / "roles"
_VALID_OWNERS: Final = frozenset({"maintainer", *(p.stem for p in _ROLES_DIR.glob("*.md"))})
_PERMITTED_OWNERS_RE: Final = re.compile(r"^Permitted owners:\s*(.+)$", re.MULTILINE)

#: RL-1046 §B (`docs/rulings/RL-01046-the-alias-class-the-disclosed-rows-and-the-run-s-
#: conditional-window.md`; cited by file path, never as "Ruling 105" — `docs/REDIRECTS.csv`
#: maps that number to this file, and after the migration the bare number resolves to a
#: different ruling entirely, RL-01059): "`(h1)` passes when every `audit-docs.py` failure
#: class on the migrated snapshot is zero except checks 29, 30 and 35, which the row prints
#: by count, each labelled `owner: W37-10`, and which do not set the exit code."
#:
#: **That quoted label ranges over §B's own class and not over F92's** (RL-1075). §B's
#: class is the unstamped-scope population this check's note reports separately; F92's is
#: the narrower set the helper below detects. Two populations share one note, and the
#: `owner:` label belongs to the first. F92's own row (`docs/findings/register.md`) names
#: its population precisely: `.claude/skills/*/SKILL.md` plus `.claude/agents/*.md` —
#: "which carry front matter a stamp must merge into" — whose owner of record is **W37-11**
#: per that row, reassigned from W37-6 on 2026-09-03. They are deferred rather than
#: hand-stamped here (that would be the owning slice's work, not this check's to do), and
#: never exempted via `UNSTAMPABLE_EXEMPTIONS` either (these files CAN carry a header; they
#: already do, just not an RFC-937 one).
#: F92's owner of record, as `docs/findings/register.md`'s F92 row states it in its
#: Work-item cell. Named as a **symbol** rather than written inline in the note below, so
#: that the test guarding the two against each other can pin one side by import instead of
#: by a pasted literal — a literal on both sides is a tautology that survives the register
#: changing underneath it (RL-1075's acceptance clause). If F92 is reassigned again, this
#: constant and the register row move together or the guard test reds, which is the point.
_F92_OWNER_OF_RECORD: Final = "W37-11"

_AGENTS_README = ".claude/agents/README.md"
_SKILL_MD_RE: Final = re.compile(r"\.claude/skills/[^/]+/SKILL\.md")


def _is_stamp_deferred_f92(path: pathlib.Path, header: object) -> bool:
    """True when `path`/`header` is a member of F92's exact deferred population: a file
    under `.claude/agents/` (its own `README.md` excepted — that one carries a real
    RFC-937 stamp, `family: reference`) or a `.claude/skills/*/SKILL.md`, whose front
    matter is Claude Code's own harness schema (`name:`/`description:`/…) rather than an
    RFC-937 header — no `family:` field populated.

    Anchored on **both** path and content, never either alone: a harness-schema file
    parked outside these two locations is not F92's population (path), and a file at one
    of these two locations that DOES carry `family:` — a future, properly stamped agent
    or skill — is not harness-schema-shaped any more and is not deferred either (content).
    That second clause is what keeps this predicate from silently widening as files here
    get migrated one at a time: the day a skill or agent file is stamped, it drops out of
    this set on its own and check 35 checks it like any other document.

    `header` is typed `object` rather than `_docid.Header`: `_docid` is loaded by path
    (`_load_module`, above), so mypy sees it only as `types.ModuleType`, and this
    function's only use of `header` is `.family`, read via `getattr` for exactly that
    reason.
    """
    if getattr(header, "family", None):
        return False
    try:
        rel = path.relative_to(REPO).as_posix()
    except ValueError:
        return False
    if rel == _AGENTS_README:
        return False
    if rel.startswith(".claude/agents/"):
        return True
    return bool(_SKILL_MD_RE.fullmatch(rel))


def readme_owner_allowlist(readme: pathlib.Path) -> frozenset[str] | None:
    """A directory README's own declared owner allow-list, read from a line
    `Permitted owners: a, b, c` — the one convention this recognises. Returns `None` (no
    clause to enforce) when the README does not state one: no fixed format is specified
    by RFC-937 anywhere, and `docs/_templates/README.md` / `docs/process/README.md` do
    not exist yet (`docs/ READMEs` is Slice W37-10's to write) — inventing a required
    format now would be enforcing a document ahead of the slice that writes it.
    """
    m = _PERMITTED_OWNERS_RE.search(readme.read_text(encoding="utf-8"))
    if m is None:
        return None
    return frozenset(name.strip() for name in m.group(1).split(","))


# -----------------------------------------------------------------------------------------
# F83 — the register of files that cannot carry a header at all, and the check that keeps
# it honest. Filed as `docs/findings/FD-01020-63-in-scope-files-cannot-carry-a-header-and-their-
# custody-is-an-exemption-rather-than-a-sidecar.md`; ruled by the maintainer 2026-09-02.
#
# Two conditions bind the exemption, and both are enforced here:
#
#   1. Every entry cites its reason and the ruling that permits it — "an exemption list
#      whose entries carry no justification is indistinguishable from a list of things
#      nobody got round to". `UnstampableExemption` makes both fields structural, so an
#      entry cannot be added without stating them.
#   2. The register is itself checked against the tree, so it cannot grow silently.
#      `_check_unstampable_register` implements this, and — per F83's own words, which are
#      RL-985's property applied to an exemption rather than a census — it **names**
#      every file on each side of the disagreement and never compares two totals. Two
#      errors that cancel pass a total-only check; `.claude/skills/docs-audit`
#      §"a total validates the total, and nothing else" records the day that happened here.
#
# F83 words condition 2 as "the count of *unstamped* in-scope files must equal the exempt
# list". `unstamped` and `unstampable` coincide only after the migration W37-6 performs.
# Measured over `git ls-files` with `nt0019_stamp_set` and `unstampable_reason` below as
# the predicate. At `359936b`: **416** files = **51** stamped + **362** with no `---` block
# + **3** carrying one that will not parse, so **365** unstamped against **65** that can
# never be stamped. **The total drifts with every markdown file added anywhere under
# `docs/`** — it was 415 at `f61f9a4` and 417 once `docs/findings/FD-01024-widening-id-scope-roots-
# reaches-no-non-markdown-file-so-62-of-the-65-exempt-files-stay-invisible-to-checks-30-39.md` lands
# — so
# it is given with its tree and its parts, never bare: parts that are stated can be summed,
# and that is the only check on a decomposition which cannot itself be a proxy. **Check 35's
# own note prints the live figures every run and is the copy to trust**; a comment restating
# a number the gate computes is how the two drift apart (`RFC-756`).
#
# The predicate that carries F83's intent across that boundary is therefore
# **cannot be stamped**, not "has not yet been": it is equivalent to F83's wording the
# moment the migration lands, and it is the only one of the two that is live, and
# falsifiable, before then. The live figures are printed by check 35's own note on every
# run, which is the copy to trust — this one is a fixed measurement at a named tree, and
# a comment restating a number the gate computes is how the two drift apart
# (`RFC-756`).
#
# **Check 35's own owner clause is a no-op for every one of the 65, not merely for the
# headerless ones.** `check_owner` skips on `header is None` *and* on `HeaderError`, so
# the three vendored manifests — which do have a `---` block, one that will not parse —
# are skipped by the second branch exactly as the 62 headerless files are skipped by the
# first. F83's disposition, "a `generated: true` exemption in check 35", therefore
# discharges nothing on its own; the register had to bring its own enforcement, which is
# what `_check_unstampable_register` and `_check_scope_unstamped_are_registered` are.
# `test_check_35_owner_clause_is_a_no_op_for_every_registered_file` pins the claim
# against the real register rather than leaving it as a reading of the code.
#
# **Both halves of the W37-6 wiring this note used to defer are now done, and this is the
# record of what changed.** It read: check 30 must consult `UNSTAMPABLE_EXEMPTIONS` when
# the scope widens, and *"widening the roots is not by itself enough"* — a scope widened
# to `docs/` reached 3 of the 65 and none of the 62 non-markdown files, because
# `_id_scope_documents` expanded a directory root with `rglob("*.md")`. That was `F87`.
#
# `_id_scope_documents` now expands a directory root through `_docid.stamp_set_files`,
# the filesystem face of the same RFC-937 §4 step 5 predicate `nt0019_stamp_set` reads —
# one definition, two consumers, held to each other by
# `test_the_two_stamp_set_consumers_read_one_definition`. So a widened scope reaches all
# 65, and check 30 consults the register (see its own body) rather than redding on every
# one of them. **Neither change moves the enforced scope on its own**: `_ID_SCOPE_ROOTS`
# is still S1's two paths, so both are inert until the roots widen — which is the point,
# a mechanism proven before the irreversible commit rather than inside it
# (`test_the_widened_scope_selector_reaches_every_registered_file`).
# -----------------------------------------------------------------------------------------

#: `scripts/file-census.py`'s `git_ls_files`. The corpus is `git ls-files`, never a
#: working-tree walk — `scripts/doc-id.py` records why this repository settled on that: a
#: walk picks up `.venv/`, `graphify-out/` and anything else untracked, which differs
#: between two checkouts of the same commit. Loaded by path for the same reason `_docid`
#: and `doc-index` above are: a hyphenated filename is not a legal `import` target.
_FILE_CENSUS_PATH: Final = REPO / "scripts" / "file-census.py"
_file_census = _load_module("_file_census_for_audit_docs", _FILE_CENSUS_PATH)

def nt0019_stamp_set(tracked: Sequence[str] | None = None) -> list[str]:
    """Every tracked file in RFC-937's stamp set, as repo-relative posix paths.

    The set is RFC §4's ruling
    (`docs/plans/PL-00967-rfc-the-readme-row-the-cell-extent-rule-and-4-step-5-s-stamp-set.md` §4,
    "§4 step 5 governs the stamp set"): every file under `docs/`, `.claude/roles/`,
    `.claude/skills/*/SKILL.md` and `.claude/agents/`, plus every `README.md` in the tree.

    That last clause is **derived from what §5.2 reaches** (`scripts/doc-id.py`'s
    `_candidate_header_paths` globs `tree_root.rglob("README.md")`) rather than copied from
    the RFC's table of six named files. The two disagree: `.claude/rfcs/README.md` is
    tracked, is outside every listed root, and is not in the RFC's six. Deriving the rule
    rather than pasting its enumeration is what makes that visible instead of inherited.

    `tracked` is injectable so a test can put a corpus in front of this without a
    filesystem; `None` means "ask git", which is the only form production uses.
    """
    if tracked is None:
        tracked = list(_file_census.git_ls_files(REPO))
    stamp_set: list[str] = _docid.nt0019_stamp_set(tracked)
    return stamp_set


def unstampable_reason(rel: str) -> str | None:
    """Why the tracked file `rel` cannot carry a governed header, or `None` when it can.

    Two disqualifiers, and only two:

    * **Not markdown.** A YAML front-matter block is a markdown convention. Prepending one
      to JSON, YAML or CSV does not produce a file with a header; it produces a file that
      no longer parses as what it is.
    * **A vendored manifest whose own front matter will not parse.** `is_vendored` alone is
      not enough — a vendored manifest that parses is stampable and stays in scope. The
      conjunction is deliberate: a *non*-vendored file that fails to parse is a defect to
      fix, not a file to exempt, and must stay a hard failure.
    """
    if not rel.endswith(".md"):
        return "not a markdown file — a YAML front-matter block would invalidate it"
    path = REPO / rel
    if not _docid.is_vendored(path, REPO):
        return None
    try:
        _docid.parse_header(path)
    except _docid.HeaderError as exc:
        return f"vendored manifest whose upstream front matter does not parse: {exc}"
    return None


def check_owner() -> None:
    """35. `owner:` is a role filename under `.claude/roles/`, or `maintainer`, and one
    the directory's `README.md` permits (RFC-937 §1.11).

    The second clause enforces only where a directory `README.md` actually exists and
    states a permitted-owner list (see `readme_owner_allowlist`) — neither of
    `_ID_SCOPE_ROOTS`'s two directories carries one today.

    F92's deferred population (`_is_stamp_deferred_f92`) is counted, never checked against
    `_VALID_OWNERS`. Its **owner of record is W37-11**, per F92's row in
    `docs/findings/register.md`; it is non-fatal here under RL-1046 §B, which ruled the
    *disclosure* — that the class is reported by count and does not set the exit code — and
    not the owner (RL-1075). The count is printed by the note below rather than stated
    here, because a pasted count is what goes stale (`CLAUDE.md` §13).
    """
    found: dict[str, list[tuple[str, str]]] = {}
    deferred = 0
    for path in _governed_documents():
        try:
            header = _docid.parse_header(path)
        except _docid.HeaderError:
            continue
        if header is None:
            continue
        if _is_stamp_deferred_f92(path, header):
            deferred += 1
            continue
        rel = path.relative_to(REPO).as_posix()
        msgs = _owner_problems(path, rel)
        if msgs:
            found[rel] = [(m, m) for m in msgs]
    notes.append(
        f"check 35: {deferred} owner check(s) deferred (F92's stamp-deferred population, owner "
        f"{_F92_OWNER_OF_RECORD} per docs/findings/register.md; non-fatal here under RL-1046 §B)"
    )
    _residue_gate(
        "check 35",
        found,
        lambda old, tmp: _owner_problems(old, old.relative_to(tmp).as_posix()),
    )


def _owner_problems(path: pathlib.Path, rel: str) -> list[str]:
    """Every check-35 problem in one governed document: an owner that is not a role file
    or 'maintainer', or not in its directory README's permitted-owner list."""
    try:
        header = _docid.parse_header(path)
    except _docid.HeaderError:
        return []
    if header is None:
        return []
    if header.owner not in _VALID_OWNERS:
        return [
            f"check 35: {rel}: owner {header.owner!r} is not a role filename under "
            f".claude/roles/ or 'maintainer' ({sorted(_VALID_OWNERS)})"
        ]
    readme = path.parent / "README.md"
    if readme.is_file():
        allow_list = readme_owner_allowlist(readme)
        if allow_list is not None and header.owner not in allow_list:
            return [
                f"check 35: {rel}: owner {header.owner!r} is not in "
                f"{readme.relative_to(REPO).as_posix()}'s permitted-owner list "
                f"{sorted(allow_list)}"
            ]
    return []


# =========================================================================================
# Check 36 — Redirects (RL-988/DP-2). Renamed and repurposed from the retired
# `check_notes_tombstone` (slot 30 -> 36; RFC-937 §5.5).
# =========================================================================================

#: RL-988 §2: RFC-937 §7 acceptance item (d) and this check are "one rule at two
#: times", so both read this **one** shared pattern-and-exclusion constant, defined once
#: in `scripts/_docid.py` (stdlib, already imported by both scripts) rather than kept here
#: as a private copy — `_docverify.py`'s `D_ALTERNATIVES` reads the identical tuple.
#: RL-988 §2 Part 1's anchoring (every entry a COMPLETE legacy identifier or path,
#: never a proper prefix) is documented at the definition, not repeated here.
LEGACY_FORM_PATTERNS: Final[tuple[tuple[str, re.Pattern[str]], ...]] = (
    _docid.LEGACY_FORM_PATTERNS
)

#: RL-988 Part 2: the bounded, load-bearing exclusion list — the residue after Part 1's
#: pattern fix, permitted only for a file whose *function* is to carry legacy forms as
#: data, never a path the migration is required to rewrite. `REDIRECTS.csv` is "already in
#: the item"; `was:` lines (wherever they appear) are handled separately below, by line,
#: not by path, since a `was:` line can appear inside an otherwise-checked file.
#:
#: The seven `tests/fixtures/docs-migration/` entries below are W37-5's — RL-988 §2's
#: own residue class names exactly this: "the fixtures ... of the migration". Each is
#: here only because its *discovery-defining* content — the thing that makes the fixture
#: recognisable as its legacy shape at all, not incidental prose — is itself a legacy
#: form: an ADR's own `ADR-703` title, a note's own `RFC-711` title, a multi-ruling
#: file's own `## Ruling N` headings, the roadmap fixture's own `W1-1`/`W1-2` row keys, the
#: spec fixture's own `**FR-XXX-N**`-shaped bold ids, and the vendored-skill pair's shared
#: `FR-XXX-N`-shaped citation (respelled schematically, 2026-09-04, RL-1044 §5.1's fence
#: clause extended to row (d): the literal worked example is itself a §7(d) alternative
#: match; RFC-937 §1.5's own stated property under test: a vendored manifest's citations
#: rewrite, a file beneath it does not — needs the same token on
#: both sides of that boundary to prove the difference). Sixteen files carried a legacy
#: form before this list was written; sweeping away *incidental* prose citations (a
#: comment saying "RFC-937 §4 step 2", not tested by anything) — the same fix RL-988
#: Part 1 applied to the pattern itself, applied here to the fixture corpus — got that
#: down to these seven; see `tests/test_audit_docs_ids.py`'s load-bearing proof for each.
LEGACY_FORM_EXCLUDED_PATHS: Final[tuple[str, ...]] = (
    "docs/REDIRECTS.csv",
    # The fixture corpus is frozen at its pre-migration shape -- that shape is what
    # `migrate()` operates on -- so these two carry the legacy family names, not the
    # post-migration ones `docs/findings/register.md`-style paths would suggest.
    "tests/fixtures/docs-migration/docs/adr/0001-example-decision.md",
    "tests/fixtures/docs-migration/docs/notes/0001-example-note.md",
    "tests/fixtures/docs-migration/docs/plans/2026-08-12-example-rulings.md",
    "tests/fixtures/docs-migration/docs/roadmap.md",
    "tests/fixtures/docs-migration/docs/specs/00-overview.md",
    "tests/fixtures/docs-migration/.claude/skills/vendored-example-skill/SKILL.md",
    "tests/fixtures/docs-migration/.claude/skills/vendored-example-skill/references/extra.md",
)

_WAS_LINE_RE: Final = re.compile(r"^\s*was:\s")

#: `docs/rulings/RL-01060-check-36-is-one-rule-at-two-times-with-d-and-must-carry-d-s-disclosed-
#: classes-check-32-s-padding-resolution-clause-adopts-e-s-conjuncts-from-docid-not-a-private-re-
#: typing.md` Entry 1 item 1:
#: `_docid.TEST_MODULE_EXCLUSIONS`' three names — the
#: instrument's own id-grammar/check/migrate test modules, which carry legacy-form ids as
#: literal fixture data by construction (the "3c tuple" the ruling names). Read alone,
#: never through `_docid.sweep_exclusion_reason`: that function also folds in
#: `LOCKFILE_EXCLUSIONS` and `FIXTURE_CORPUS_ROOTS`, and check 36's own
#: `LEGACY_FORM_EXCLUDED_PATHS` above already carves the seven `tests/fixtures/
#: docs-migration/` files back in **individually**, by design, to prove each is load
#: bearing (`test_check_36_w37_5_fixture_exclusions_are_load_bearing`); folding in the
#: *root*-level `FIXTURE_CORPUS_ROOTS` exclusion here would swallow that whole design —
#: every file the per-file allowlist means to test would stop reaching the sweep at all.
_TEST_MODULE_EXCLUDED_PATHS: Final[frozenset[str]] = frozenset(
    name for name, _reason in _docid.TEST_MODULE_EXCLUSIONS
)


@dataclass(frozen=True)
class _LegacyFormHit:
    rel: str
    lineno: int
    label: str
    token: str

    def __str__(self) -> str:
        return f"{self.rel}:{self.lineno}: {self.label} {self.token!r}"


def _sweep_legacy_form_hits(
    paths: Iterable[pathlib.Path],
    *,
    repo_root: pathlib.Path = REPO,
    excluded_paths: Sequence[str] = LEGACY_FORM_EXCLUDED_PATHS,
    patterns: Sequence[tuple[str, re.Pattern[str]]] = LEGACY_FORM_PATTERNS,
) -> list[_LegacyFormHit]:
    """Every legacy (pre-migration) id or path form found across `paths`, outside a
    `was:` line, outside a fenced code block, outside `excluded_paths`, outside the
    instrument's own test-module fixture data (`_TEST_MODULE_EXCLUDED_PATHS`), outside
    a family's own split-source index (`_docid.is_split_source_index`,
    2026-09-05, rows (d9)-(d12)'s Check-36 alignment), and outside the generated-
    contract tier (`_docid.generated_contract_tier_reason`, F103, 2026-09-17, the narrow
    predicate rather than the full `_docid.sweep_exclusion_reason` — that also folds in
    `FIXTURE_CORPUS_ROOTS`, which would swallow the per-file fixture allowlist below
    whole): the same generated JSON/YAML `_docverify.tracked_files` already excludes from
    the migration's own (d)/(e)
    verification corpus, read by the identical shared predicate rather than a private
    re-typing of `generate-contracts.py`'s paths — F103 named exactly this scope mismatch,
    check 36 scanning a tier the migration instrument itself never treats as residue — RFC-937
    §7 acceptance item (d) and check 36's third clause are "one rule at two times"
    (RL-988 §2), so both read the identical `_docid` predicates: the fence
    (`_docid.fenced_line_numbers`, the same rule row (e)'s `padded_hits` and row (d)'s own
    corpus apply), the pattern tuple (`_docid.LEGACY_FORM_PATTERNS`), the test-module
    exclusion (`_docid.TEST_MODULE_EXCLUSIONS`, row (d)'s `tracked_files` applies via
    `_docid.sweep_exclusion_reason`), and the split-index exclusion (row (d)'s own
    `_path_alternative_verdict` in `_docverify.py` excludes the identical file for the
    identical reason: `docs/<family>/INDEX.md`'s `` `was:` `` table column and "became N
    documents" heading are RL-287/RL-255's ruled provenance, generated whole with no
    other kind of line ever written there, so a file-level exclusion is still correct
    here rather than the "classify per line, never per path" rule elsewhere in this
    module). Structured, so a caller can classify each hit
    against (d)'s disclosed-class predicates before deciding what is fatal — `check_redirects`
    below does exactly that; `sweep_legacy_forms` renders these to strings for every
    existing caller and test.

    Explicit parameters, never the module constants read implicitly, so a later slice's
    migration acceptance can call this unscoped over `git ls-files` for (d), and so a test
    can prove each exclusion entry is load-bearing by calling this with it removed
    (RL-988 §4 item 1) and prove the positive control by calling this with the shipped
    constants unmodified (§4 item 2: "never a re-typed copy of the pattern").
    """
    excluded = frozenset(excluded_paths)
    hits: list[_LegacyFormHit] = []
    for path in paths:
        try:
            rel = path.relative_to(repo_root).as_posix()
        except ValueError:
            rel = path.as_posix()
        if (
            rel in excluded
            or rel in _TEST_MODULE_EXCLUDED_PATHS
            or _docid.is_split_source_index(rel)
            or _docid.generated_contract_tier_reason(rel) is not None
            # W37-6 h1-check36 follow-up, 2026-09-17: the governance-record class
            # (`_docid.governance_record_reason`) — e.g.
            # `docs/research/file-census-<sha>.csv`, whose per-file `path` column is a
            # full per-file dump of the tree at the commit its own name names
            # (GOVERNANCE_RECORD_EXCLUSIONS) — quotes legacy pre-migration forms as the
            # record's own evidence, never a survivor for this sweep to flag. Read
            # through the identical narrow predicate `generated_contract_tier_reason`
            # above already uses, not the full `_docid.sweep_exclusion_reason` (that
            # also folds in `FIXTURE_CORPUS_ROOTS`, which would swallow the per-file
            # fixture allowlist this function's docstring names).
            or _docid.governance_record_reason(rel) is not None
        ):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        fenced = _docid.fenced_line_numbers(text)
        for i, line in enumerate(text.splitlines()):
            if i in fenced or _WAS_LINE_RE.match(line):
                continue
            for label, pattern in patterns:
                for m in pattern.finditer(line):
                    hits.append(_LegacyFormHit(rel, i + 1, label, m.group(0)))
    return hits


def sweep_legacy_forms(
    paths: Iterable[pathlib.Path],
    *,
    repo_root: pathlib.Path = REPO,
    excluded_paths: Sequence[str] = LEGACY_FORM_EXCLUDED_PATHS,
    patterns: Sequence[tuple[str, re.Pattern[str]]] = LEGACY_FORM_PATTERNS,
) -> list[str]:
    """`_sweep_legacy_form_hits` above, rendered to `"{rel}:{lineno}: {label} {token!r}"`
    strings — this module's and every test's existing contract, unchanged."""
    return [
        str(hit)
        for hit in _sweep_legacy_form_hits(
            paths, repo_root=repo_root, excluded_paths=excluded_paths, patterns=patterns
        )
    ]


def _legacy_form_disclosure_reason(hit: _LegacyFormHit, *, repo_root: pathlib.Path) -> str | None:
    """Why `hit` is excluded from check 36's fatal count — or `None` when it is a real
    `token_map` miss. RFC-937 §7 acceptance item (d) already discloses these classes
    (`_docverify.rows_d`); check 36 reads the identical `_docid` predicates rather than
    retyping them, so the same text gets the same verdict from both checks.
    """
    if hit.label in _docid.DISCLOSED_ALIAS_LABELS:
        return "alias class — RL-1043 §4 / RL-1046 §A"
    if hit.label == _docid.SCOPED_REQUIREMENT_ID_LABEL and _docid.is_scoped_id_never_allocated(
        hit.token, definition_root=repo_root, redirect_root=repo_root
    ):
        return "never-allocated closed class — deputy's mechanical predicate, 2026-09-04"
    return None


def check_redirects() -> None:
    """36. Redirects (RFC-937 §1.11) — renamed and repurposed from the retired
    `check_notes_tombstone` (slot 30 -> 36; see this module's docstring). Three clauses:

    1. Every `was:` field on an in-scope header has a `docs/REDIRECTS.csv` row.
    2. Every `docs/REDIRECTS.csv` row's `new_path` exists.
    3. No pre-migration form (`sweep_legacy_forms` above) survives in scope outside the
       CSV and `was:` lines.

    `docs/REDIRECTS.csv` does not exist pre-migration (created in Slice W37-6), so
    clauses 1-2 are vacuous today by construction — nothing in scope carries a `was:`
    field either. **Clause 3 is gated on the same file for a different reason**, found
    empirically rather than predicted: the sweep asks whether a legacy form survives
    *instead of* its new one, which presupposes the new corpus exists. Before that, a
    legitimate citation to a not-yet-renumbered thing is indistinguishable from a
    survivor by pattern alone — document-ids.md's own lift of RFC-937 cites `RFC-897`,
    `RFC-896`, `RFC-756` and `RL-943` in its prose and names `docs/audit/` describing
    its own dissolution, and the unscoped sweep reds on all five the moment it runs
    unconditionally. This is the same self-match class RL-988 diagnosed in RFC-937 §7
    (d)'s own text (the bare `NT-00` fragment); the fix there was the pattern, the fix
    here is the gate — a citation to a real, currently-correct id is not itself a legacy
    *form* no matter how careful the pattern is, until there is a new form for it to have
    failed to become. Once `docs/REDIRECTS.csv` exists, clause 3 replaces the old
    `.claude/notes/` tombstone-content check over the whole of `_ID_SCOPE_ROOTS`.
    """
    redirects_path = ROOT / "REDIRECTS.csv"
    redirect_rows: list[dict[str, str | None]] = []
    if redirects_path.is_file():
        with redirects_path.open(newline="", encoding="utf-8") as fh:
            redirect_rows = list(csv.DictReader(fh))
        for row in redirect_rows:
            new_path = row.get("new_path") or ""
            if new_path and not (REPO / new_path).exists():
                fail(
                    f"check 36: REDIRECTS.csv row for {row.get('old_id')}: "
                    f"{new_path!r} does not exist"
                )

    was_values: set[str] = set()
    for path in _governed_documents():
        try:
            header = _docid.parse_header(path)
        except _docid.HeaderError:
            continue
        if header is not None and header.was:
            was_values.add(header.was)

    redirected_olds = {row.get("old_path") or "" for row in redirect_rows} | {
        row.get("old_id") or "" for row in redirect_rows
    }
    for was in was_values:
        if was not in redirected_olds:
            fail(f"check 36: `was: {was}` has no docs/REDIRECTS.csv row")

    if not redirects_path.is_file():
        # The sweep is a *post*-migration invariant: it asks whether a legacy form
        # survives outside the CSV and `was:` lines, which presupposes the CSV and the
        # new forms exist to survive *instead of*. Before that, a legitimate citation to
        # a not-yet-renumbered thing (document-ids.md's own lift of RFC-937 cites RFC-897,
        # RFC-896, RFC-756 and RL-943 in its prose, and names `docs/audit/` describing
        # its own dissolution) is indistinguishable from a survivor by pattern alone —
        # exactly the self-match class RL-988 diagnosed in RFC-937 §7 (d) itself,
        # discovered here by running the sweep rather than predicted. `REDIRECTS.csv`'s
        # existence is the migration's own marker, the same role `docs/INDEX.md` plays
        # for check 32's gate.
        legacy_hits: list[_LegacyFormHit] = []
        notes.append(
            "check 36: no docs/REDIRECTS.csv yet — the legacy-form sweep is a "
            "post-migration invariant and is skipped until it exists (pre-migration, "
            "every citation in scope is to a currently-correct, not-yet-renumbered id)"
        )
    else:
        legacy_hits = _sweep_legacy_form_hits(_governed_documents())

    # ADR 8449: scoped to the governed families; a legacy form this change introduces fails,
    # one that was already there is counted by `_residue_gate`.
    fatal_hits = 0
    found: dict[str, list[tuple[str, str]]] = {}
    disclosed_by_class: collections.Counter[str] = collections.Counter()
    for hit in legacy_hits:
        reason = _legacy_form_disclosure_reason(hit, repo_root=REPO)
        if reason is None:
            fatal_hits += 1
            found.setdefault(hit.rel, []).append(
                (f"{hit.label}|{hit.token}", f"check 36: {hit}")
            )
        else:
            disclosed_by_class[f"{hit.label} ({reason})"] += 1

    def _at_base(old: pathlib.Path, tmp: str) -> list[str]:
        return [
            f"{h.label}|{h.token}"
            for h in _sweep_legacy_form_hits([old], repo_root=pathlib.Path(tmp))
            if _legacy_form_disclosure_reason(h, repo_root=REPO) is None
        ]

    _residue_gate("check 36", found, _at_base)

    disclosed_total = sum(disclosed_by_class.values())
    disclosed_text = (
        "; ".join(f"{n} {cls}" for cls, n in sorted(disclosed_by_class.items()))
        if disclosed_by_class
        else "none"
    )
    notes.append(
        f"check 36: {len(redirect_rows)} redirect row(s), {len(was_values)} `was:` "
        f"field(s) in scope, {len(legacy_hits)} legacy-form hit(s) "
        f"({fatal_hits} fatal, {disclosed_total} disclosed — "
        "docs/rulings/RL-01060-check-36-is-one-rule-at-two-times-with-d-and-must-carry-d-s-"
        "disclosed-classes-check-32-s-padding-resolution-clause-adopts-e-s-conjuncts-from-"
        "docid-not-a-private-re-typing.md "
        f"Entry 1 item 1, same predicates as RFC-937 §7(d)): {disclosed_text}"
    )


# =========================================================================================
# Check 37 — shape: required ## sections per family template.
# =========================================================================================

_SECTION_HEADING_RE: Final = re.compile(r"^##\s+(.+?)\s*$")

# Rulings 96 and 97 (`docs/plans/2026-09-03-w37-6-d1-d2-rulings.md`) — the detector is
# **asymmetric** and the required set **excludes placeholder headings**.
#
# Template side: `##` exactly, as before. Document side: any depth, with a leading `N. `
# / `N.N. ` ordinal stripped, because every real ruling numbers its subsections
# (`### 4. Acceptance — …`) and a depth-agnostic *literal* match still finds nothing
# (`docs/findings/FD-01027-check-37-reds-on-95-of-95-post-migration-rulings-unconditional-on-the-
# flag-day-because-its-section-detector-cannot-see-a-level-heading.md` §B).
#
# The asymmetry is not a convenience. Making the **template** side depth-agnostic too
# would newly require `SL-NNNNN — <Title>` and `WK-NNNNN — <Title>` — the only body
# headings `docs/_templates/SL.md` and `WK.md` declare, both `###` and both pure
# placeholder. That is a requirement no document can satisfy, latent today only because
# the corpus holds zero `slice`/`work` documents. `_PLACEHOLDER_RE` closes the same trap
# from the other side: a template heading whose text is not a constant cannot be a
# required literal.
_ORDINAL_PREFIX_RE: Final = re.compile(r"^\d+(?:\.\d+)*\.\s+")
_ANY_DEPTH_HEADING_RE: Final = re.compile(r"^#{1,6}\s+(.+?)\s*$")
_PLACEHOLDER_RE: Final = re.compile(r"<[^<>]+>|N{4,}")


def _document_body_sections(path: pathlib.Path) -> set[str]:
    """Every heading text in a *document*, at any depth, with a leading ordinal stripped.

    The document side of check 37's asymmetric match. Unlike `_template_body_sections`
    this reads instances, not sources, so it deliberately does not strip a leading
    comment block: a governed document has front matter, not a template comment.
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if lines and lines[0] == "---":
        closing = next((i for i, line in enumerate(lines[1:], 1) if line == "---"), None)
        if closing is not None:
            lines = lines[closing + 1 :]
    out: set[str] = set()
    for line in lines:
        m = _ANY_DEPTH_HEADING_RE.match(line)
        if m:
            out.add(_ORDINAL_PREFIX_RE.sub("", m.group(1)))
    return out


def _template_body_sections(path: pathlib.Path) -> tuple[str, ...]:
    """The `##`-level heading texts in one template's body (after its own header block or
    leading comment) — check 37's own "required sections", generalised from every
    family's template rather than hand-listed. No template's own body heading uses a
    `<Title>`/`NNNNN` placeholder (verified by reading all thirteen), so a literal
    string match against a real document's own `##` headings is exact.
    """
    text = path.read_text(encoding="utf-8")
    stripped = _LEADING_COMMENT_RE.sub("", text, count=1)
    lines = stripped.splitlines()
    if lines and lines[0] == "---":
        try:
            closing = lines.index("---", 1)
            body = lines[closing + 1 :]
        except ValueError:
            body = lines
    else:
        body = lines
    sections = []
    for line in body:
        m = _SECTION_HEADING_RE.match(line)
        if m:
            sections.append(m.group(1))
    return tuple(sections)


def required_sections(family: str) -> tuple[str, ...]:
    """`family`'s required `##` sections, derived from its template — empty for a family
    whose template declares none (`reference`: "RFC-937 does not prescribe this family's
    body shape"), which means nothing is required, not that the check is skipped.

    A missing template file is check 30's own failure to report (`derive_field_policies`
    asserts the full manifest); this returns `()` rather than raising, so a vanished
    template reds once, clearly, instead of also crashing check 37 before checks 38-39
    get to run.
    """
    for template_name, template_family in _TEMPLATE_FAMILY.items():
        if template_family == family:
            try:
                declared = _template_body_sections(_TEMPLATES_DIR / template_name)
            except OSError:
                return ()
            # RL-1040: a heading whose text is not a constant cannot be a required literal.
            # `## Verified first, at <tree>` in `RL.md` names a real section of the
            # ruling shape, but its text carries the tree and so differs between documents
            # (measured at `15ed00d`: 40 occurrences over 94 ruling blocks, 18 distinct
            # texts). It stays in the template, as the shape an author
            # copies; it is not something check 37 can match.
            return tuple(s for s in declared if not _PLACEHOLDER_RE.search(s))
    return ()


def check_shape() -> None:
    """37. Shape: a document carries every `##` section its family's template body
    declares — the ten-section spec rule, generalised (RFC-937 §1.11).
    """
    checked = 0
    exempt = 0
    for path in _id_scope_documents():
        try:
            header = _docid.parse_header(path)
        except _docid.HeaderError:
            continue
        if header is None:
            continue
        checked += 1
        if header.was is not None:
            # RL-1039: check 37 governs documents **authored from a template**. A body the
            # migration carried over verbatim from a pre-standard file predates the shape
            # it would be judged against, and `was:` is how the migration says so — RFC-937
            # §1.5's closed field set, `docs/rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-
            # integer-identity-a-self-describing-layout-and-roles-per-family.md:125`,
            # `was: 2026-08-18-profile-contract.md   # migration only`. It is set only on
            # the migration's own write paths and is declared in **no** template, so a
            # later author cannot inherit the exemption by copying one.
            exempt += 1
            continue
        needed = required_sections(header.family)
        if not needed:
            continue
        present = _document_body_sections(path)
        missing = [s for s in needed if s not in present]
        if missing:
            fail(
                f"check 37: {path.relative_to(REPO).as_posix()}: missing required "
                f"section(s) {missing} for family {header.family!r}"
            )
    notes.append(
        f"check 37: {checked} document(s) checked in scope, {exempt} exempt as "
        f"verbatim-migrated (`was:`), {checked - exempt} shape-checked"
    )


# =========================================================================================
# Check 38 — loop signal, warn-only. Never fails the gate.
# =========================================================================================


def check_ids_30_39() -> None:
    """Run every RFC-937 id-standard check (30-39) — one function per the plan's own
    "ten broken-input proofs, one per check" framing, called together here so `main`
    keeps one call site the way it already does for `check_notes` (16-20).
    """
    check_header_fields()
    check_id_filename_directory()
    check_citations()
    check_cross_references()
    check_freeze()
    check_owner()
    check_redirects()
    check_shape()


_SPEC_FENCE_RE: Final = re.compile(r"^\s{0,3}```(?P<info>.*)$")
_EXAMPLE_MARKER_RE: Final = re.compile(
    r"^json (?:schema=(?P<schema>[A-Z]\w*)|(?P<illustrative>illustrative))$"
)


@dataclass(frozen=True)
class SpecFence:
    """One fenced block of a spec; `tests/test_spec_examples.py` loads this parser by path."""

    path: pathlib.Path
    line: int
    info: str
    body: str

    @property
    def language(self) -> str:
        return self.info.split(" ", 1)[0]

    @property
    def schema(self) -> str | None:
        marker = _EXAMPLE_MARKER_RE.match(self.info)
        return marker["schema"] if marker else None

    @property
    def illustrative(self) -> bool:
        marker = _EXAMPLE_MARKER_RE.match(self.info)
        return bool(marker and marker["illustrative"])


def spec_fences(path: pathlib.Path) -> list[SpecFence]:
    """Every fenced block, indented ones included: a list-indented fence is still a fence."""
    lines = path.read_text(encoding="utf-8").splitlines()
    fences: list[SpecFence] = []
    i = 0
    while i < len(lines):
        opening = _SPEC_FENCE_RE.match(lines[i])
        if opening is None:
            i += 1
            continue
        j = i + 1
        while j < len(lines) and _SPEC_FENCE_RE.match(lines[j]) is None:
            j += 1
        fences.append(SpecFence(path, i + 1, opening["info"].strip(), "\n".join(lines[i + 1 : j])))
        i = j + 1
    return fences


def check_spec_examples(specs: list[pathlib.Path]) -> None:
    """Check 40: every fence declares a language; every json block is marked (FD-1381)."""
    total = schema = illustrative = unmarked = 0
    for spec in specs:
        for block in spec_fences(spec):
            where = f"{block.path.name}:{block.line}"
            if not block.language:
                fail(f"check 40: {where}: a fence declares no language")
                continue
            if block.language != "json":
                continue
            total += 1
            if block.schema:
                schema += 1
                try:
                    json.loads(block.body)
                except ValueError as exc:
                    fail(f"check 40: {where}: schema={block.schema} does not parse: {exc}")
            elif block.illustrative:
                illustrative += 1
            else:
                unmarked += 1
                fail(f"check 40: {where}: json block has no schema= or illustrative marker")
    notes.append(
        f"check 40: {total} json blocks: {schema} schema, {illustrative} illustrative, "
        f"{unmarked} unmarked"
    )


def main() -> int:
    md = sorted(f for f in ROOT.rglob("*.md") if not _is_frozen_file(f))
    specs = sorted(ROOT.glob("specs/*.md"))

    # 1. relative links
    for f in md:
        for m in re.finditer(r"\[[^\]]*\]\(([^)#\s]+)(#[^)]*)?\)", f.read_text(encoding="utf-8")):
            target = m.group(1)
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            if not (f.parent / target).resolve().exists():
                # `check N: <path>: <prose>` — see check 36's identical fix above; PR
                # #758's `_docverify._h1_residue_by_file` extraction needs the path
                # immediately after the check number, not after descriptive prose.
                # `REPO`, not `ROOT` (=`REPO / "docs"`): every other check names its
                # file relative to the repo root, and a path relative to `docs/` instead
                # (`rulings/RL-....md`, missing the `docs/` prefix) does not resolve from
                # the repo root at all — a reader handed it cannot find the file. Found
                # by `_docverify._h1_residue_by_file`'s resolution-against-the-corpus
                # check (pin-3, PR #756/#758/#759's own follow-up): the old shape-only
                # extractor accepted these 235 tokens because they looked path-shaped,
                # never checking they named a real file.
                fail(f"check 1: {f.relative_to(REPO)}: broken link to {target}")

    # 2/3. requirement ids
    defined: dict[str, list[str]] = collections.defaultdict(list)
    for f in specs:
        for m in _REQ_DEFINED.finditer(f.read_text(encoding="utf-8")):
            defined[m.group(1)].append(f.name)
    for rid, where in defined.items():
        if len(where) > 1:
            fail(f"check 2: {rid} defined in multiple specs: {where}")

    # A filed plan is written *before* the spec change it argues for, so it names the id it
    # intends to take — "Next free: `FR-68`" — which by definition is not yet defined.
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
            for m in _REQ_CITED.finditer(cited):
                referenced[m.group(1)].add(str(f.relative_to(ROOT)))
    for rid in sorted(set(referenced) - set(defined)):
        fail(f"check 2: {rid} referenced but never defined (in {sorted(referenced[rid])})")

    # Numbering. Two regimes, and which one applies is read off the ids themselves, not
    # assumed: a module-scoped id (`FR-154`) belongs to a per-module sequence that must
    # be contiguous, while a global-sequence id (`FR-1187`, RFC-937 D1/D2) is drawn from one
    # allocator shared with every other family, so gaps in the FR run are not merely legal --
    # they are what a shared sequence looks like, and asserting contiguity over it would red
    # on every correctly-numbered tree. Contiguity of the *global* sequence is
    # `doc-id.py check`'s (RFC-937 §7(b)); what is left here is uniqueness, checked above.
    scoped = {rid for rid in defined if _SCOPED_REQ_ID.fullmatch(rid)}
    by_prefix: dict[str, list[int]] = collections.defaultdict(list)
    for rid in scoped:
        prefix, num = rid.rsplit("-", 1)
        by_prefix[prefix].append(int(num))
    for prefix, nums in sorted(by_prefix.items()):
        missing = sorted(set(range(1, max(nums) + 1)) - set(nums))
        if missing:
            fail(f"check 3: {prefix} has numbering gaps: {missing}")
    notes.append(
        f"requirement numbering: {len(scoped)} module-scoped id(s) across "
        f"{len(by_prefix)} per-module sequence(s) checked for contiguity; "
        f"{len(defined) - len(scoped)} global-sequence id(s) checked for uniqueness only "
        "(contiguity is `doc-id.py check`'s)"
    )

    notes.append(f"{len(defined)} requirements defined across {len(specs)} specs")

    #: spec filename -> the module code that spec's own header declares. `00-overview.md`'s
    #: §7.1 is where the vocabulary is defined; every spec repeats its own code in its status
    #: line. A spec with no such line keeps its filename as the label rather than being
    #: silently dropped from coverage.
    module_of: dict[str, str] = {}
    for f in specs:
        m = re.search(r"\*\*Module code:\*\*\s*`([A-Z]+)`", f.read_text(encoding="utf-8"))
        if m:
            module_of[f.name] = m.group(1)
        else:
            fail(
                f"check 14: {f.relative_to(ROOT)}: no `**Module code:** \u0060XXX\u0060` "
                "in its status line — check 14 groups workflow coverage by it"
            )

    # 4. (retired by ADR 8449: the open-question mirror. Each spec's §10 is the home of its
    #    questions; docs/open-questions.md is frozen.)

    # 5. ADRs
    #
    # Both layouts, discovered from disk: `docs/adrs/0001-*.md` before the RFC-937 migration,
    # `docs/adrs/ADR-00004-*.md` after it. Numbers are compared as **integers** so neither
    # the file's padding nor the citation's decides whether a real ADR resolves.
    adrs = {int(m.group(1)) for p in ROOT.glob("adrs/0*.md") if (m := _ADR_FILE.match(p.name))}
    adrs |= {int(m.group(1)) for p in ROOT.glob("adrs/*.md") if (m := _ADR_FILE.match(p.name))}
    corpus = "\n".join(f.read_text(encoding="utf-8") for f in md)
    for ref in sorted({int(n) for n in _ADR_CITED.findall(corpus)} - adrs):
        fail(f"check 5: ADR-{ref} referenced but no file exists")
    notes.append(f"{len(adrs)} ADR(s) on disk, every ADR citation in docs/ resolves")

    # 6. spec sections
    for f in specs:
        heads = re.findall(r"^## \d+\.?\s*(?:—\s*)?(.+)$", f.read_text(encoding="utf-8"), re.M)
        lowered = [h.lower() for h in heads]
        for name in REQUIRED_SECTIONS:
            key = name.lower().split("(")[0].strip()
            if not any(key in h for h in lowered):
                fail(f"check 6: {f.name} missing required section: {name}")

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
            fail(f"check 7: {f.relative_to(ROOT)}: {exc}")

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
                fail(f"check 8: {src.relative_to(ROOT)}: local $ref {ref} does not resolve")
            return
        elif ref.startswith(("http://", "https://")):
            return  # external, not our concern
        else:
            tail = ref
        target, _, fragment = tail.partition("#")
        path = (schema_root / target) if ref.startswith(_ABS_PREFIX) else (src.parent / target)
        path = path.resolve()
        if path not in loaded:
            fail(f"check 8: {src.relative_to(ROOT)}: $ref {ref} -> missing {target}")
        elif fragment and not resolve_pointer(loaded[path], fragment):
            fail(f"check 8: {src.relative_to(ROOT)}: $ref {ref} -> fragment does not resolve")

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
                    f"check 9: {f.relative_to(ROOT)}: reference to {code} §{sec} — "
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
                    f"check 10: error code {code} claimed by both {owner[code]} and "
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
            # DEP-537: GOV's audit sink and permission check are cross-cutting interfaces
            if other == "GOV" and re.search(r"audit|permission|authoris|authoriz|RBAC", row, re.I):
                continue
            fail(
                f"check 11: {f.name}: DEP-1 violation — {me} consumes from {other}, "
                "which is to its right"
            )

    # 12. money discipline: *_minor fields must never be fractional.
    #: FR-23, not FR-10. FR-10 governs values and is scoped to the rating path and
    #: persisted rate tables, so it does not reach a diagnostic; the reserved *name* is
    #: FR-23 and is unscoped, which is the rule this check actually applies. It named
    #: FR-10 until 2026-08-24, when FR-23 was written down (OQ-539).
    money_re = re.compile(r'"(\w*_minor)"\s*:\s*(-?\d+\.\d+)')
    for f in list(md) + schemas:
        for m in money_re.finditer(f.read_text(encoding="utf-8")):
            fail(
                f"check 12: {f.relative_to(ROOT)}: {m.group(1)} written as fractional "
                f"{m.group(2)} (FR-23)"
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
                f"check 13: {f.name}: glossary term '{t}' is already defined in "
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
        # The module comes from the **spec that defines the requirement**, read off that
        # spec's own `Module code:` line, not from a segment of the id. Post-migration there
        # is no module segment left in an id (RFC-937 D2), so `rid.split("-")[1]` returned
        # the *number*: coverage was reported per requirement — "356 100%, 357 0%, 358 0%",
        # 450 buckets of one — and the 10% floor then fired or did not fire on individual
        # requirements. The id stopped carrying the module; the file always did.
        mod = module_of.get(defined[rid][0], defined[rid][0])
        per_mod[mod][1] += 1
        if re.search(rf"\b{re.escape(rid)}\b", wf_text):
            per_mod[mod][0] += 1
    summary = []
    for mod in sorted(per_mod):
        hit, tot = per_mod[mod]
        ratio = hit / tot if tot else 1.0
        summary.append(f"{mod} {ratio:.0%}")
        if ratio < coverage_floor:
            fail(f"check 14: workflow coverage for {mod} is {ratio:.0%} ({hit}/{tot}), below "
                 f"the {coverage_floor:.0%} floor — no user journey exercises this module")
    notes.append("workflow coverage: " + ", ".join(summary))

    # 21. journey citations resolve to a declared interface (FR-19, OQ-543)
    #
    # `scope-audit.py --endpoints` compares a spec's §5.1 table against the published
    # contract. This is the same idea one level up: the **journeys** cite endpoints and
    # `pricing-core` functions, and a journey citing something no spec declares is drift
    # nothing else in this repository can see. `audit-docs.py` check 14's "workflow coverage"
    # measures whether a journey *mentions* a requirement id, which is a different and much
    # weaker question — the one plan review 2 found it was answering.
    #
    # It earned its place on the first run: WF-698 A8 cited `profile_version()`, and `01`
    # §5.2 was corrected to `profile_frame` / `profile_parquet` on 2026-08-15 without the
    # journey being updated.
    declared_paths: dict[tuple[str, tuple[str, ...]], str] = {}
    for f in specs:
        for line in f.read_text(encoding="utf-8").splitlines():
            row = _docid.table_rows.endpoint_row(line)
            if row is None:
                continue
            for path in (p for p in re.findall(r"`([^`]+)`", row[1]) if p.startswith("/")):
                for method in re.split(r"`?/`?", row[0]):
                    key = (method.strip("`"), _path_segments(path))
                    declared_paths.setdefault(key, f.name)

    declared_functions: dict[str, str] = {}
    for f in specs:
        for m in re.finditer(
            r"^(?:async )?def ([a-z_][a-z0-9_]*)\(", f.read_text(encoding="utf-8"), re.M
        ):
            declared_functions.setdefault(m.group(1), f.name)

    # Both filename forms: `WF-698-dataset-to-approved-model.md` before the RFC-937 migration,
    # `WF-00979-dataset-to-approved-model.md` after it. `glob` is case-sensitive on Linux, so
    # the lower-case pattern alone matched **zero** journeys post-migration and check 21
    # reported "0 endpoints, 0 functions, all declared" -- a pass, printed, over nothing.
    journeys = sorted(
        set(ROOT.glob("workflows/wf-*.md")) | set(ROOT.glob("workflows/WF-*.md"))
    )
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
                f"check 21: {f.name}: cites `{m.group(1)} {m.group(2)}`, which no spec "
                "declares in its §5.1 REST API table (FR-19)"
            )
        for m in re.finditer(r"`([a-z_][a-z0-9_]*)\(\)`", body):
            cited_functions += 1
            if m.group(1) not in declared_functions:
                undeclared += 1
                fail(
                    f"check 21: {f.name}: cites `pricing-core` function `{m.group(1)}()`, "
                    "which no spec declares in its §5.2 interface block (FR-19)"
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
    # `00` §5.6 declares the canonical routes (FR-25); each module's §5.3 gives the
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
                cells = _docid.table_rows.split_row(line)
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
                        f"check 24: {f.name} §5.3: no route under `{route}` declared in "
                        f"`00` §5.6 (owner {code}) — fix {f.name} §5.3 (`00` §5.6 is "
                        "canonical)"
                    )
            elif route not in s53:
                fail(
                    f"check 24: {f.name} §5.3: route `{route}` declared in `00` §5.6 "
                    f"(owner {code}) has no matching row — fix {f.name} §5.3 (`00` §5.6 "
                    "is canonical)"
                )

    # 30-39. RFC-937's id-standard checks, path-scoped to _ID_SCOPE_ROOTS (Slice W37-4).
    check_ids_30_39()

    # 25. every F-nn finding id cited in docs/research/, docs/plans/ or a working note
    # resolves against the register, an archived phase register, or a closure record

    # 26. the process core extract's citations resolve in the process spec
    check_process_core_drift()

    # 27. the process core extract's recorded digest matches delivery-process.md's bytes
    check_process_core_digest()

    # 40. every spec fence declares a language; every json block declares its class (FD-1381)
    check_spec_examples(specs)

    counted = failures

    for note in notes:
        print(f"  {note}")

    if counted:
        print(f"\nFAILED ({len(counted)}):")
        for msg in counted:
            print(f"  - {msg}")
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())