#!/usr/bin/env python3
"""Consistency audit for the docs/ specification suite and the .claude/notes/ working notes.

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
 16. Every working note carries the header block .claude/notes/README.md requires.
 17. Note numbering is well-formed and unique, and matches each file's own heading.
 18. The notes index and the directory agree, in both directions.
 19. Every reference a note makes resolves — links, FR-/NFR- ids, OQ- ids, ADRs, NT- ids.
 20. No note defines a requirement id; only docs/specs/ may do that.
 21. Every endpoint and pricing-core function a workflow journey cites is declared
     in the owning module's §5.1 or §5.2 (FR-OVR-17, OQ-OVR-6).
 22. Every markdown table row has its own header's cell count — catching a literal
     `|` inside a cell, which shifts every column after it while still rendering.

Usage: python3 scripts/audit-docs.py
"""
from __future__ import annotations

import collections
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
ROOT = REPO / "docs"
NOTES = REPO / ".claude" / "notes"
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


def check_notes(defined: set[str], questions: set[str], adrs: set[str]) -> None:
    """16-20. The working notes in .claude/notes/, against that directory's README.

    The notes are not the specification, so most of their audit standard is judgement — is
    this status still true of the repository, is this deliverable still right for the phase
    the project is now in. A script cannot answer either. What it *can* answer is every
    mechanical part, and those are precisely the ones that rot without anyone noticing: a
    reference to a file that has been renamed, a number reused after a deletion, an index
    that no longer lists what the directory holds.

    Two limits are worth stating rather than implying. **Number reuse across a deletion is
    not detectable here** — a snapshot cannot see the retired number, so that check stays
    manual and stays in the README. And gaps in the sequence are *legal*: a deleted note
    retires its number, so contiguity is deliberately not asserted.
    """
    if not NOTES.is_dir():
        notes.append("no .claude/notes/ directory — checks 16-20 skipped")
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
        fail(".claude/notes/README.md is missing — the index is part of the standard")
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
            fail(f"{rel(path)} is not listed in the .claude/notes/README.md index")
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
        fail(f"index lists note NT-{number}, but no such file exists in .claude/notes/")

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
    notes.append(f"{len(in_file)} open questions, all mirrored")

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
                fail(
                    f"error code {code} claimed by both {owner[code]} and "
                    f"{f.name} — annotate one as '(re-raised from `NN`)' or "
                    "give ownership to one module"
                )
            owner.setdefault(code, f.name)
    notes.append(f"{len(owner)} error codes, ownership exclusive")

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
        for m in re.finditer(r"^def ([a-z_][a-z0-9_]*)\(", f.read_text(encoding="utf-8"), re.M):
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

    # 16-20. the working notes in .claude/notes/
    check_notes(set(defined), in_file, adrs)

    # 23. every spec §10 mirror row carries the register's status for that question
    check_open_question_mirror_status(specs)

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