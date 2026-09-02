#!/usr/bin/env python3
"""Generate `docs/INDEX.md` — NT-0019 §1.4's "one row per id, rows and documents alike".

`docs/plans/2026-09-01-nt-0019-id-standard-map-plan.md`, Slice W37-3. Three things this
script generates, none of them hand-editable (`CLAUDE.md` §2's model-schema rule applied to
governance data instead of API shapes):

1. **The index itself** — one row per governed id, built by walking the document-family
   directories (`plans/`, `ledgers/`, `rulings/`, …) through `scripts/_docid.py`'s
   `parse_header`, plus the row families (`FR`/`NFR`/`DEP`/`OQ` bold ids in spec-style
   tables, `WK`/`SL` fenced blocks under roadmap headings) that `parse_header` cannot reach
   because it parses one whole file's leading front matter, never a record embedded
   mid-document. A row block's own grammar is deliberately *local* to this module
   (`_parse_row_block` below) rather than reaching into `scripts/_docid.py`'s private
   helpers: only `Header`, `HeaderError`, `parse_header`, `canonical`, `padded`,
   `family_of`, `is_vendored` and the constants are that module's published surface
   (this slice's own instruction: "adds no second parser" is about not re-implementing
   *file-level* front-matter parsing a second, divergent way — `parse_header` still owns
   that; a row block is a different, smaller grammar `parse_header` cannot reach at all).

2. **The `execution` column** (NT-0019 §1.7) — *derived, never stored*. A `PL-` file's own
   `status:`/`kind:` only ever says `draft | active | superseded | retired`; whether it was
   *executed* lives in whether an `LG-`/`SL-`/`CR-` elsewhere says so. `derive_execution`
   below is the literal implementation of §1.7's seven-row table, and no `Header` field
   anywhere in this module is ever assigned an execution value — see
   `test_doc_index.py::test_no_header_field_carries_an_execution_value`.

3. **The ownership matrix** (§1.6) — one row per *role*, not per family, because that is the
   only shape in which "the reporter and the watcher own no governed document" is a stated
   fact (an empty row) rather than an absence a reader has to notice on their own. Derived by
   inverting a hardcoded transcription of §1.6's "Owner — creates & amends" column: a role's
   owned-family list is every family whose owner cell mentions that role by name. Reporter
   and watcher are never mentioned in that column anywhere in the note, so their rows come
   out empty *by derivation*, the same "catches a real disagreement" property `CLAUDE.md`
   §13 asks of a generated artifact — add either role to a cell by mistake and the empty row
   disappears on the next run, rather than needing a maintainer to notice a hand-written list
   went stale.

**Two interpretations this module makes where NT-0019 is silent, flagged for the record**
(the slice's dispatch: "If the cut turns out to have a dependency it did not name, tell me"):

- **A map plan's "slices' leaf plans"** (§1.7's roll-up line) has no header field naming the
  linkage — `plans:` is ledger-only. This module uses the field that *is* shared: every
  `kind: leaf` plan carrying the same `work:` as the map plan. That is well-founded (a leaf
  plan's `slice:` resolves to an `SL-` row under the same `work:` the map plan itself
  carries) but is this module's inference, not a quoted rule.
- **Findings carry neither `phase:` nor `work:`** in §1.5's own field-applicability comment
  ("phase: ... # every WK, SL, PL, LG, RL, CR, RS" — `FD` is absent from both lists), so
  the phase report's "findings opened vs discharged" element (§1.10 (c)) cannot be scoped to
  one phase from the header fields alone. Reported project-wide instead, labelled as such.

Usage:
    python3 scripts/doc-index.py [--root PATH]              # (re)generate docs/INDEX.md
    python3 scripts/doc-index.py [--root PATH] --check       # exit 1 if regeneration would
                                                              # change the file on disk
    python3 scripts/doc-index.py [--root PATH] --show ID     # print one record's fields,
                                                              # including `execution` for PL
    python3 scripts/doc-index.py [--root PATH] --phase P<n>  # print the §1.10 (c) report

`--root` defaults to `docs` and exists so the test suite can point this at
`tests/fixtures/docs-ids/w37-3-corpus` instead — the slice's own scope note: "`doc-index.py`
is built here but cannot be run against the live corpus until W37-6, because before the
migration there are no ids to index."
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location("_docid", REPO / "scripts" / "_docid.py")
assert _spec is not None
assert _spec.loader is not None
_docid = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _docid  # dataclasses needs the module in sys.modules
_spec.loader.exec_module(_docid)

Header = _docid.Header
HeaderError = _docid.HeaderError
parse_header = _docid.parse_header
ID_RE = _docid.ID_RE
canonical = _docid.canonical
padded = _docid.padded
family_of = _docid.family_of
STATUS_WORDS = _docid.STATUS_WORDS

# NT-0019 §1.4's directory-is-the-family rule, document families only — row families
# (FR/NFR/DEP, OQ, WK, SL) are scanned separately below because they are records embedded
# in a shared file, not one file per id.
FAMILY_DIRS: dict[str, str] = {
    "WF": "workflows",
    "ADR": "adrs",
    "RFC": "rfcs",
    "PL": "plans",
    "LG": "ledgers",
    "RL": "rulings",
    "RS": "research",
    "CR": "closures",
    "FD": "findings",
}

_ROW_HEADING_FIELDS = ("id", "family", "title", "status", "phase", "work")
_PHASE_SECTION_FIELDS = ("status", "opened", "target", "gates", "exit criteria", "works")


# ---------------------------------------------------------------------------------------
# Corpus: every governed id in a tree, indexed for the lookups execution derivation and the
# phase report both need.
# ---------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Record:
    """One `INDEX.md` row's worth of data — a `Header`, plus the two things a `Header`
    alone cannot carry: which file it came from (for the phase report's citation scan) and
    its raw body text (ditto).
    """

    header: Header
    path: Path
    body: str


def _normalize_id(raw: str) -> str:
    m = ID_RE.fullmatch(raw.strip())
    if not m:
        return raw.strip()
    prefix, n = m.groups()
    return canonical(prefix, int(n))


class Corpus:
    def __init__(self, records: list[Record]) -> None:
        self.records = records
        self._by_id: dict[str, Record] = {}
        for r in records:
            if r.header.id is None:
                continue
            self._by_id[_normalize_id(r.header.id)] = r

    def by_id(self, ref: str | None) -> Record | None:
        if ref is None:
            return None
        return self._by_id.get(_normalize_id(ref))

    def headers(self) -> list[Header]:
        return [r.header for r in self.records]

    def ledger_for_plan(self, plan_id: str) -> Header | None:
        norm = _normalize_id(plan_id)
        candidates = [
            r.header
            for r in self.records
            if r.header.family == "ledger"
            and norm in {_normalize_id(p) for p in r.header.plans}
        ]
        for status in ("active", "closed"):
            for h in candidates:
                if h.status == status:
                    return h
        return candidates[0] if candidates else None

    def closure_cites_work(self, work_id: str | None) -> bool:
        if work_id is None:
            return False
        norm = _normalize_id(work_id)
        return any(
            r.header.family == "closure" and r.header.work is not None
            and _normalize_id(r.header.work) == norm
            for r in self.records
        )

    def rulings_for_work(self, work_id: str) -> list[Header]:
        norm = _normalize_id(work_id)
        return [
            r.header
            for r in self.records
            if r.header.family == "ruling" and r.header.work is not None
            and _normalize_id(r.header.work) == norm
        ]

    def superseded_plans_for_work(self, work_id: str) -> list[Header]:
        norm = _normalize_id(work_id)
        return [
            r.header
            for r in self.records
            if r.header.family == "plan"
            and r.header.work is not None and _normalize_id(r.header.work) == norm
            and r.header.status == "superseded"
        ]

    def slices_for_work(self, work_id: str) -> list[Header]:
        norm = _normalize_id(work_id)
        return [
            r.header
            for r in self.records
            if r.header.family == "slice"
            and r.header.work is not None and _normalize_id(r.header.work) == norm
        ]


# ---------------------------------------------------------------------------------------
# Scanning: document families (one file == one record) and row families (many records in
# one shared file).
# ---------------------------------------------------------------------------------------


def scan_document_family(root: Path, subdir: str) -> list[Record]:
    directory = root / subdir
    if not directory.is_dir():
        return []
    out = []
    for path in sorted(directory.glob("*.md")):
        header = parse_header(path)
        if header is None:
            continue
        out.append(Record(header=header, path=path, body=path.read_text(encoding="utf-8")))
    return out


def _fenced_yaml_blocks(text: str) -> list[tuple[int, int, list[str]]]:
    """Every ` ```yaml ... ``` ` block's (nearest preceding heading level, 1-based start
    line of its content, content lines). Used for both roadmap row blocks (WK-/SL-, under a
    `###`+ heading) and the phase section's own field block (under a `##` heading) — the
    same fence convention throughout this file, one fixed grammar (§1.5's flat `key: value`
    lines), never a second one; the heading level is what tells the two apart, since a
    phase's own block uses a disjoint field set (`_PHASE_SECTION_FIELDS`) from a row's.
    """
    lines = text.splitlines()
    blocks: list[tuple[int, int, list[str]]] = []
    heading_level = 0
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith("#"):
            heading_level = len(stripped) - len(stripped.lstrip("#"))
        if stripped == "```yaml":
            start = i + 1
            j = start
            content: list[str] = []
            while j < len(lines) and lines[j].strip() != "```":
                content.append(lines[j])
                j += 1
            blocks.append((heading_level, start + 1, content))
            i = j + 1
        else:
            i += 1
    return blocks


# The scalar fields a `WK-`/`SL-` row actually carries — a strict subset of §1.5's full
# closed field set (no `plans:`, no `supersedes:`, … — those are document-family-only in
# practice for these two row families). Kept local to this module rather than imported
# from `scripts/_docid.py`, which exposes no shared row-block parser (verified against
# W37-2's actual implementation).
_ROW_FIELDS = frozenset(
    {"id", "family", "kind", "title", "status", "created", "owner", "phase", "work", "slice"}
)


def _parse_row_block(content: list[str], path: Path, base_lineno: int) -> dict[str, str]:
    """A minimal, local `key: value` parser for one `WK-`/`SL-` fenced row block. Not
    shared with `scripts/_docid.py`: that module's published surface is `Header`,
    `HeaderError`, `parse_header`, `canonical`, `padded`, `family_of`, `is_vendored` and the
    constants — nothing else is contracted, so this slice does not depend on its internals.
    """
    raw: dict[str, str] = {}
    for offset, line in enumerate(content):
        if not line.strip():
            continue
        lineno = base_lineno + offset
        key, sep, value = line.partition(":")
        if not sep:
            raise HeaderError(f"{path}:{lineno}: not a 'key: value' line: {line!r}")
        key = key.strip()
        if key not in _ROW_FIELDS:
            raise HeaderError(f"{path}:{lineno}: unknown row field {key!r}")
        if key in raw:
            raise HeaderError(f"{path}:{lineno}: duplicate row field {key!r}")
        raw[key] = value.split("#", 1)[0].strip()
    return raw


def _row_header_from_raw(raw: dict[str, str]) -> Header:
    created_raw = raw.get("created")
    return Header(
        id=raw.get("id"),
        family=raw.get("family", ""),
        kind=raw.get("kind"),
        title=raw.get("title", ""),
        status=raw.get("status", ""),
        created=date.fromisoformat(created_raw) if created_raw else None,
        owner=raw.get("owner", ""),
        phase=raw.get("phase"),
        work=raw.get("work"),
        slice_=raw.get("slice"),
        tree=None,
        plans=(),
        supersedes=(),
        superseded_by=None,
        corrected_by=(),
        corrects=None,
        relates=(),
        was=None,
        vendored=False,
        origin=None,
        extra={},
    )


def scan_roadmap_rows(path: Path) -> list[Record]:
    """`WK-`/`SL-` rows: each is a heading followed by its own fenced field block (§1.5:
    "as a fenced block under the row's heading"). Phase sections (`## P<n> — ...`) are
    skipped here — they carry no id (§1.1 rule 4) — and read separately by
    `scan_phase_sections`.
    """
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    out = []
    for heading_level, base_lineno, content in _fenced_yaml_blocks(text):
        if heading_level < 3:
            continue  # a `##` phase-section block, not a `###`+ row block
        raw = _parse_row_block(content, path, base_lineno)
        if "id" not in raw or raw.get("family") not in ("work", "slice"):
            continue
        header = _row_header_from_raw(raw)
        out.append(Record(header=header, path=path, body="\n".join(content)))
    return out


@dataclass(frozen=True)
class PhaseSection:
    phase: str
    title: str
    status: str
    works: tuple[str, ...]
    fields: dict[str, str]


def scan_phase_sections(path: Path) -> list[PhaseSection]:
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    sections = []
    heading_re = re.compile(r"^##\s+(P\d+[a-z]?)\s+—\s+(.+)$")
    for idx, line in enumerate(lines):
        m = heading_re.match(line.strip())
        if not m:
            continue
        phase_id, title = m.group(1), m.group(2)
        # The next fenced block belongs to this heading.
        rest = "\n".join(lines[idx + 1 :])
        blocks = _fenced_yaml_blocks(rest)
        if not blocks:
            continue
        _heading_level, _base_lineno, content = blocks[0]
        raw: dict[str, str] = {}
        for cline in content:
            if not cline.strip():
                continue
            key, sep, value = cline.partition(":")
            if not sep:
                continue
            key = key.strip()
            if key not in _PHASE_SECTION_FIELDS:
                continue
            raw[key] = value.split("#", 1)[0].strip()
        works_raw = raw.get("works", "")
        works = tuple(w.strip() for w in works_raw.split(",") if w.strip())
        sections.append(
            PhaseSection(
                phase=phase_id,
                title=title,
                status=raw.get("status", ""),
                works=works,
                fields=raw,
            )
        )
    return sections


_BOLD_ID_ROW = re.compile(
    r"^\|\s*\*\*(FR|NFR|DEP|OQ)-(\d+)\*\*\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|"
)


def scan_bold_id_rows(path: Path) -> list[Record]:
    """`FR-`/`NFR-`/`DEP-`/`OQ-` rows: a bold id in the spec's own table, never a fenced
    header (§1.6: "Requirement rows keep the spec's bold-id convention; their fields are
    the spec table's columns"). This reads a 4-column `| **PREFIX-n** | title | status |`
    shape — the shape this slice's own fixture corpus uses — because NT-0019 does not pin
    one before the migration restructures the real spec tables (W37-6); full fidelity
    against the live corpus is that slice's to prove, not this one's (this slice's own
    scope note).
    """
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    out = []
    for line in text.splitlines():
        m = _BOLD_ID_ROW.match(line)
        if not m:
            continue
        prefix, n, title, status = m.groups()
        header = Header(
            id=canonical(prefix, int(n)),
            family=family_of(prefix),
            kind=None,
            title=title,
            status=status,
            created=None,
            owner="",
            phase=None,
            work=None,
            slice_=None,
            tree=None,
            plans=(),
            supersedes=(),
            superseded_by=None,
            corrected_by=(),
            corrects=None,
            relates=(),
            was=None,
            vendored=False,
            origin=None,
            extra={},
        )
        out.append(Record(header=header, path=path, body=line))
    return out


def build_corpus(root: Path) -> Corpus:
    records: list[Record] = []
    for subdir in FAMILY_DIRS.values():
        records.extend(scan_document_family(root, subdir))
    records.extend(scan_roadmap_rows(root / "roadmap.md"))
    records.extend(scan_bold_id_rows(root / "open-questions.md"))
    for spec_path in sorted((root / "specs").glob("*.md")) if (root / "specs").is_dir() else []:
        records.extend(scan_bold_id_rows(spec_path))
    return Corpus(records)


# ---------------------------------------------------------------------------------------
# The execution column (NT-0019 §1.7) — derived, never stored.
# ---------------------------------------------------------------------------------------


def derive_execution(header: Header, corpus: Corpus) -> str | None:
    """The literal implementation of §1.7's seven-row table. Returns `None` for anything
    that is not a plan — execution is a `PL-`-only concept.
    """
    if header.family != "plan":
        return None
    if header.kind in ("review", "handover"):
        return "terminal"
    if header.status == "superseded":
        return f"superseded → {header.superseded_by}"
    if header.status == "retired":
        sl = corpus.by_id(header.slice_)
        if sl is None or sl.header.status == "retired":
            return "retired"
        return "retired"  # self-declared status is authoritative; check 33 audits the pair
    if header.kind == "map":
        return _rollup_map_plan(header, corpus)
    return _derive_leaf_execution(header, corpus)


def _closure_covers(header: Header, corpus: Corpus) -> bool:
    """A `CR-` cites the plan's `slice:`/`work:` — read as: the `CR-` (which only ever
    carries `work:`, never `slice:`) cites the *work* this plan's slice belongs to, or the
    plan's own `work:` directly when it has no slice (a map plan). §1.5's field table gives
    `CR-` no `slice:` at all, so "cites the plan's slice:" cannot mean a literal field match.
    """
    work_id = header.work
    if header.slice_ is not None:
        sl = corpus.by_id(header.slice_)
        if sl is not None and sl.header.work is not None:
            work_id = sl.header.work
    return corpus.closure_cites_work(work_id)


def _derive_leaf_execution(header: Header, corpus: Corpus) -> str:
    sl = corpus.by_id(header.slice_)
    lg = corpus.ledger_for_plan(header.id) if header.id else None
    if _closure_covers(header, corpus) and sl is not None and sl.header.status == "closed":
        return "closed"
    if lg is not None and lg.status == "closed":
        return "executed"
    if (lg is not None and lg.status == "active") or (
        sl is not None and sl.header.status == "active"
    ):
        return "in progress"
    return "not started"


def _rollup_map_plan(header: Header, corpus: Corpus) -> str:
    """"A map plan rolls up from its slices' leaf plans" (§1.7). No header field names a
    map plan's children directly (`plans:` is ledger-only), so this module uses the field
    that *is* shared: every `kind: leaf` plan carrying the same `work:` — see this file's
    module docstring for why that is well-founded rather than assumed.
    """
    children = [
        r.header
        for r in corpus.records
        if r.header.family == "plan"
        and r.header.kind == "leaf"
        and r.header.work is not None
        and header.work is not None
        and _normalize_id(r.header.work) == _normalize_id(header.work)
    ]
    if not children:
        return "not started"
    states = [derive_execution(c, corpus) for c in children]
    if any(s == "in progress" for s in states):
        return "in progress"
    if all(s == "closed" for s in states):
        return "closed"
    if all(s in ("closed", "executed") for s in states):
        return "executed"
    return "not started"


# ---------------------------------------------------------------------------------------
# The ownership matrix (NT-0019 §1.6) — one row per role, derived by inversion.
# ---------------------------------------------------------------------------------------

# §1.6's "Owner — creates & amends" column, transcribed once. Not byte-identical prose (only
# `document-ids.md`, W37-1, lifts §1 verbatim) — kept close enough that every role name
# appearing in the note's own column also appears here, which is what the derivation below
# depends on.
_OWNERSHIP_TABLE: tuple[tuple[str, str], ...] = (
    ("requirement (FR/NFR/DEP)", "decision-maker, via spec-change"),
    ("open question (OQ)", "decision-maker records (anyone raises)"),
    ("phase", "maintainer opens the section; lead maintains it"),
    ("work (WK)", "maintainer opens (draft); planner writes its map plan; maintainer sets active"),
    ("slice (SL)", "planner, cut in the map plan (draft)"),
    ("workflow (WF)", "decision-maker, via spec-change"),
    ("decision (ADR)", "decision-maker, via adr-write (draft)"),
    ("proposal (RFC)", "maintainer mints and owns; any role drafts on instruction; lead assesses"),
    ("plan (PL map/leaf)", "planner, via writing-plans"),
    ("plan (PL review)", "auditor"),
    ("plan (PL handover)", "executor"),
    ("ledger (LG)", "executor, appends per task and per PR (active)"),
    ("ruling (RL)", "decision-maker; the maintainer may author one on scope or process"),
    ("research (RS spike/measurement)", "executor (library-spike, measurements)"),
    ("research (RS audit)", "auditor"),
    ("closure (CR)", "auditor (work, phase); lead (review)"),
    ("finding (FD)", "auditor (register row + essay)"),
    ("reference: process/", "maintainer"),
    ("reference: charters", "maintainer"),
    ("reference: skills", "the five roles already permitted; lead approves"),
    ("reference: agents", "lead"),
    ("reference: contracts/", "generated from model-schema; executor via contract-schema"),
)

# NT-0019 §1.6's own role vocabulary, in the order the process spec introduces them
# (`.claude/roles/*.md`). Every role appears as a row even when it owns nothing — the
# reporter and the watcher, explicitly, per §1.6's closing paragraph.
ROLES: tuple[str, ...] = (
    "decision-maker", "maintainer", "planner", "executor", "auditor", "lead",
    "reporter", "watcher",
)


def ownership_matrix() -> dict[str, tuple[str, ...]]:
    """Role -> the families whose §1.6 "Owner" cell names that role. `reporter` and
    `watcher` are named in no cell (verified: neither string appears anywhere in
    `_OWNERSHIP_TABLE`'s second column), so both come out as `()` — the two deliberately
    empty rows, produced by derivation rather than special-cased.
    """
    matrix: dict[str, list[str]] = {role: [] for role in ROLES}
    for family_label, owner_text in _OWNERSHIP_TABLE:
        for role in ROLES:
            if role in owner_text:
                matrix[role].append(family_label)
    return {role: tuple(families) for role, families in matrix.items()}


# ---------------------------------------------------------------------------------------
# The phase report (NT-0019 §1.10 (c) / Acceptance Standard item 10).
# ---------------------------------------------------------------------------------------


def _all_citations(corpus: Corpus, phase_path: Path) -> set[str]:
    """Every id cited by any file's raw text (header fields and body alike) or by
    `roadmap.md`'s own prose, excluding a record's citation of itself. `INDEX.md` is not
    part of the source corpus this reads, so "outside INDEX.md" holds by construction.
    """
    cited: set[str] = set()
    texts: list[tuple[str | None, str]] = [(r.header.id, r.body) for r in corpus.records]
    if phase_path.is_file():
        texts.append((None, phase_path.read_text(encoding="utf-8")))
    for self_id, text in texts:
        self_norm = _normalize_id(self_id) if self_id else None
        for prefix, n in ID_RE.findall(text):
            norm = canonical(prefix, int(n))
            if norm != self_norm:
                cited.add(norm)
    return cited


def phase_report(corpus: Corpus, phase_id: str, root: Path) -> str:
    sections = scan_phase_sections(root / "roadmap.md")
    section = next((s for s in sections if s.phase == phase_id), None)
    works = list(section.works) if section else []

    lines = [f"# Phase report — {phase_id}", ""]

    # 1. Works closed and retired.
    work_headers = [corpus.by_id(w) for w in works]
    closed_works = [w.header for w in work_headers if w and w.header.status == "closed"]
    retired_works = [w.header for w in work_headers if w and w.header.status == "retired"]
    lines.append(
        f"1. Works closed and retired: {len(closed_works)} closed "
        f"({', '.join(h.id or '' for h in closed_works) or '—'}), "
        f"{len(retired_works)} retired "
        f"({', '.join(h.id or '' for h in retired_works) or '—'})"
    )

    # 2. Slices planned versus delivered.
    all_slices = [s for w in works for s in corpus.slices_for_work(w)]
    delivered = [s for s in all_slices if s.status == "closed"]
    lines.append(
        f"2. Slices planned versus delivered: {len(all_slices)} planned, "
        f"{len(delivered)} delivered"
    )

    # 3. Plans superseded per Work.
    lines.append("3. Plans superseded per Work:")
    for w in works:
        superseded = corpus.superseded_plans_for_work(w)
        lines.append(f"   - {w}: {len(superseded)}")

    # 4. Rulings per Work.
    lines.append("4. Rulings per Work:")
    for w in works:
        rulings = corpus.rulings_for_work(w)
        lines.append(f"   - {w}: {len(rulings)}")

    # 5. Findings opened versus discharged, with the unowned-decay count.
    # Project-wide: NT-0019's field-applicability comment (§1.5) lists `phase:`/`work:` as
    # carried by "every WK, SL, PL, LG, RL, CR, RS" — `FD` is absent from both lists, so
    # this element cannot be scoped to one phase from the header fields alone. See this
    # file's module docstring.
    findings = [r.header for r in corpus.records if r.header.family == "finding"]
    opened = len(findings)
    discharged = [f for f in findings if f.status in ("closed", "retired")]
    unowned_decay = [
        f for f in findings if f.status == "active" and not (f.extra.get("decision") or "").strip()
    ]
    lines.append(
        f"5. Findings opened versus discharged (project-wide — FD carries no phase/work "
        f"field to scope this by): {opened} opened, {len(discharged)} discharged, "
        f"{len(unowned_decay)} unowned-decay"
    )

    # 6. Documents with no inbound citation outside INDEX.md, among this phase's records.
    cited = _all_citations(corpus, root / "roadmap.md")
    phase_ids = {
        _normalize_id(r.header.id)
        for r in corpus.records
        if r.header.id and (r.header.phase == phase_id or r.header.id in works)
    }
    uncited = sorted(i for i in phase_ids if i not in cited)
    lines.append(
        f"6. Documents with no inbound citation outside INDEX.md: "
        f"{', '.join(uncited) or '—'}"
    )

    # 7. Days from a plan reaching active to its closure record being filed. Scoped to
    # plans whose derived `execution` is actually "closed" — a plan a `CR-` happens to
    # share a work with, but which never itself closed (superseded, terminal, still
    # running), has no "closure record being filed" to measure against.
    lines.append("7. Days from a plan reaching active to its closure record being filed:")
    plans_in_phase = [
        r.header
        for r in corpus.records
        if r.header.family == "plan"
        and r.header.phase == phase_id
        and r.header.created
        and derive_execution(r.header, corpus) == "closed"
    ]
    any_pair = False
    for p in plans_in_phase:
        work_id = p.work
        if p.slice_ is not None:
            sl = corpus.by_id(p.slice_)
            if sl is not None and sl.header.work is not None:
                work_id = sl.header.work
        if work_id is None:
            continue
        crs = [
            r.header
            for r in corpus.records
            if r.header.family == "closure" and r.header.work is not None
            and _normalize_id(r.header.work) == _normalize_id(work_id)
            and r.header.created
        ]
        for cr in crs:
            assert p.created is not None
            assert cr.created is not None
            days = (cr.created - p.created).days
            lines.append(f"   - {p.id} -> {cr.id}: {days} days")
            any_pair = True
    if not any_pair:
        lines.append("   - (none)")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------------------
# `docs/INDEX.md` rendering.
# ---------------------------------------------------------------------------------------


def _sort_key(header: Header) -> tuple[int, str]:
    m = ID_RE.fullmatch(header.id) if header.id else None
    n = int(m.group(2)) if m else -1
    return (n, header.id or "")


def render_index(corpus: Corpus) -> str:
    lines = [
        "# Index",
        "",
        "Generated by `scripts/doc-index.py`. Do not hand-edit — see NT-0019 §1.4.",
        "",
        "| id | family | kind | title | status | owner | phase | execution |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for header in sorted(corpus.headers(), key=_sort_key):
        execution = derive_execution(header, corpus) or ""
        cells = (
            header.id or "",
            header.family,
            header.kind or "",
            header.title,
            header.status,
            header.owner,
            header.phase or "",
            execution,
        )
        lines.append("| " + " | ".join(cells) + " |")

    lines.append("")
    lines.append("## Ownership matrix")
    lines.append("")
    lines.append("| role | owns |")
    lines.append("|---|---|")
    for role, families in ownership_matrix().items():
        lines.append(f"| {role} | {', '.join(families)} |")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------------------


def _show(corpus: Corpus, ref: str) -> int:
    record = corpus.by_id(ref)
    if record is None:
        print(f"no such id: {ref}", file=sys.stderr)
        return 1
    header = record.header
    print(f"id: {header.id}")
    print(f"family: {header.family}")
    print(f"kind: {header.kind or ''}")
    print(f"title: {header.title}")
    print(f"status: {header.status}")
    print(f"owner: {header.owner}")
    print(f"phase: {header.phase or ''}")
    execution = derive_execution(header, corpus)
    if execution is not None:
        print(f"execution: {execution}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO / "docs")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true", help="exit 1 if INDEX.md is stale")
    group.add_argument("--show", metavar="ID", help="print one record, with its execution")
    group.add_argument("--phase", metavar="P<n>", help="print the §1.10 (c) phase report")
    args = parser.parse_args(argv)

    corpus = build_corpus(args.root)

    if args.show:
        return _show(corpus, args.show)

    if args.phase:
        print(phase_report(corpus, args.phase, args.root), end="")
        return 0

    fresh = render_index(corpus)
    index_path = args.root / "INDEX.md"

    if args.check:
        current = index_path.read_text(encoding="utf-8") if index_path.is_file() else None
        if current != fresh:
            print(f"{index_path} is stale — run `python3 scripts/doc-index.py` to regenerate")
            return 1
        print(f"{index_path}: OK (byte-stable)")
        return 0

    if not corpus.records:
        # Caught empirically while building this slice: run with no `--root` against
        # today's pre-migration `docs/` and every file fails `parse_header`'s "no front
        # matter" test harmlessly, `build_corpus` returns zero records, and the write path
        # below would otherwise happily overwrite a real `docs/INDEX.md` with a
        # near-empty file that looks like a successful run. NT-0019's own words — "cannot
        # be run against the live corpus until W37-6, because before the migration there
        # are no ids to index" — become a refusal here rather than a silent no-op success,
        # so this cannot be run by mistake before the migration lands.
        print(
            f"refusing to write {index_path}: zero governed records found under "
            f"{args.root} — either the corpus has not been migrated to NT-0019's layout "
            "yet (see docs/plans/2026-09-01-nt-0019-id-standard-map-plan.md, Slice W37-6), "
            "or --root points at the wrong tree",
            file=sys.stderr,
        )
        return 1

    index_path.write_text(fresh, encoding="utf-8")
    print(f"wrote {index_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
