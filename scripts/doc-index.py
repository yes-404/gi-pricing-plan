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

**Two points this module first flagged as its own inference or as NT-0019 silence, both
resolved since** — by Rulings 70-72,
`docs/plans/2026-09-02-w37-field-set-and-rollup-rulings.md`, not by further guessing here:

- **The map-plan roll-up** (`_rollup_map_plan`, `_slice_child_state`) implements Ruling 72
  exactly: children are the map plan's *slices*, not a `work:` proxy over leaf plans, and
  the precedence table has **no catch-all** — an unenumerated combination raises. An
  earlier version of this function used the `work:` proxy plus a trailing
  `return "not started"`, which read a half-planned Work as `closed`, a mid-flight Work as
  `not started`, and a replanned-then-completed slice as `not started` — three confirmed
  defects, all from that one default. This module no longer claims the note is silent about
  the missing rules: it states two of the seven, and Ruling 72 states the rest.
- **The findings phase-report element** (`_parse_register`, `_findings_figures`) reads
  `findings/register.md`, never an `FD-` essay's header. This module's first cut called
  NT-0019 "silent" on scoping a finding to a phase; Ruling 71 found that claim false — the
  note says so in §5.2 and §5.4, just not in §1.5's applicability comment, which governs the
  essay's header and was never the carrier. Three figures, plus a separately labelled
  carry-in, replace the earlier single project-wide count.

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
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Final

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

#: `docs/_templates/` is a fixed governance artifact of the real repository tree — never
#: the fixture corpus a caller may point `--root` at (`build_corpus(root)` below takes a
#: fixture root for testing; the field *policy* a row or phase section is checked against
#: does not vary with that). Ruling 79 §3 item 1 / Ruling 80 §3 item 3.
_TEMPLATES_DIR: Final = REPO / "docs" / "_templates"


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


# The row-field policy used to be a hand-written frozenset here (`_ROW_FIELDS`) — a
# transcription Ruling 70 already forbids, and Ruling 79 found it wrong in both directions
# at once: too strict (rejected `tree:`/`corrected_by:`/`relates:`, which `WK.md`/`SL.md`
# both declare) and too permissive (admitted `kind:`/`slice:`, which `WK.md`'s own comment
# forbids by name). Deleted, not extended (Ruling 79 §3 item 1) — the permitted set is now
# derived per family from `docs/_templates/WK.md`/`SL.md` via `_docid.row_template_fields`,
# the one function `scripts/doc-id.py`'s row *writer* (`migrate`) also calls, so the two
# cannot silently disagree (Ruling 79 §3 items 2 and 4).


def _row_list_value(path: Path, key: str, raw_value: str) -> tuple[str, ...]:
    """A `[a, b]` row-block list value — `corrected_by:`/`relates:` (NT-0019 §1.5). The
    same flat `[a, b]` grammar `scripts/_docid.py`'s front-matter parser applies to a
    document's own `plans:`/`supersedes:`/etc., re-implemented locally rather than
    imported: that module's published surface is `Header`, `HeaderError`, `parse_header`,
    `canonical`, `padded`, `family_of`, `is_vendored` and the constants — its list parser
    is not part of that surface, the same reason `_parse_row_block`'s `key: value`
    splitting below is local too.
    """
    stripped = raw_value.strip()
    if not (stripped.startswith("[") and stripped.endswith("]")):
        raise HeaderError(
            f"{path}: row field {key!r} is not a well-formed `[a, b]` list: {raw_value!r}"
        )
    inner = stripped[1:-1].strip()
    if not inner:
        return ()
    return tuple(item.strip() for item in inner.split(","))


def _parse_row_block(
    content: list[str],
    path: Path,
    base_lineno: int,
    row_field_policy: Mapping[str, frozenset[str]],
) -> dict[str, str]:
    """A minimal, local `key: value` parser for one `WK-`/`SL-` fenced row block. Not
    shared with `scripts/_docid.py`: that module's published surface is `Header`,
    `HeaderError`, `parse_header`, `canonical`, `padded`, `family_of`, `is_vendored` and the
    constants — nothing else is contracted, so this slice does not depend on its internals.

    `row_field_policy` maps family word -> permitted field set (`_docid.row_template_fields`
    per family, computed once by the caller — Ruling 79 §3 item 1). A row's own `family:`
    value decides which policy applies, and that value is itself one of the keys being
    parsed, so validation is a second pass over an already-collected raw dict rather than
    a check inline in the first: every `key: value` line is read first (checking only
    shape and duplicates), then, once `family` is known, every key collected is checked
    against that family's permitted set. A block whose `family:` is not a recognised row
    family is returned unchecked — `scan_roadmap_rows`'s own family filter already
    discards it, and only a `work`/`slice` block is this parser's business to validate.
    """
    entries: list[tuple[int, str]] = []
    raw: dict[str, str] = {}
    for offset, line in enumerate(content):
        if not line.strip():
            continue
        lineno = base_lineno + offset
        key, sep, value = line.partition(":")
        if not sep:
            raise HeaderError(f"{path}:{lineno}: not a 'key: value' line: {line!r}")
        key = key.strip()
        if key in raw:
            raise HeaderError(f"{path}:{lineno}: duplicate row field {key!r}")
        raw[key] = value.split("#", 1)[0].strip()
        entries.append((lineno, key))

    permitted = row_field_policy.get(raw.get("family", ""))
    if permitted is not None:
        for lineno, key in entries:
            if key not in permitted:
                raise HeaderError(f"{path}:{lineno}: unknown row field {key!r}")
    return raw


def _row_header_from_raw(raw: dict[str, str], path: Path) -> Header:
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
        tree=raw.get("tree"),
        plans=(),
        supersedes=(),
        superseded_by=None,
        corrected_by=_row_list_value(path, "corrected_by", raw.get("corrected_by", "[]")),
        corrects=None,
        relates=_row_list_value(path, "relates", raw.get("relates", "[]")),
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
    row_field_policy = {
        family: _docid.row_template_fields(_TEMPLATES_DIR, family)
        for family in _docid.ROW_TEMPLATE_FILES
    }
    out = []
    for heading_level, base_lineno, content in _fenced_yaml_blocks(text):
        if heading_level < 3:
            continue  # a `##` phase-section block, not a `###`+ row block
        raw = _parse_row_block(content, path, base_lineno, row_field_policy)
        if "id" not in raw or raw.get("family") not in ("work", "slice"):
            continue
        header = _row_header_from_raw(raw, path)
        out.append(Record(header=header, path=path, body="\n".join(content)))
    return out


@dataclass(frozen=True)
class PhaseSection:
    phase: str
    title: str
    status: str
    works: tuple[str, ...]
    fields: dict[str, str]


_PHASE_HEADING_RE = re.compile(r"^##\s+(P\d+[a-z]?)\s+—\s+(.+)$")


def scan_phase_sections(path: Path) -> list[PhaseSection]:
    """`## P<n> — <title>` sections (NT-0019 §1.1 rule 4, §1.3): plain `key: value` lines
    directly beneath the heading, never a fenced block (Ruling 80,
    `docs/plans/2026-09-02-w37-template-parser-conflicts-rulings.md` — `docs/_templates/
    PHASE.md`'s own form, and `scripts/audit-docs.py`'s `_EXPECTED_NO_BLOCK_TEMPLATES`
    already enforces the same by path).

    `_docid.scan_plain_field_block` bounds the read to the lines between this heading and
    the next heading or the first non-`key: value` line, whichever comes first — never a
    lookahead to the rest of the file. That is the fix for the former `rest =
    "\n".join(lines[idx + 1:])`, which let a phase section with no fields of its own
    silently borrow whichever fenced block happened to sit somewhere below it (Ruling 80
    §3 item 2). A heading with nothing recognisable directly beneath it therefore
    contributes no `PhaseSection` at all — "must produce no phase, or a loud failure —
    never a phase built from a later block" (Ruling 80 §4 item 2) — rather than one built
    from whatever came after.
    """
    if not path.is_file():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    phase_fields = _docid.phase_template_fields(_TEMPLATES_DIR)
    sections = []
    for idx, line in enumerate(lines):
        m = _PHASE_HEADING_RE.match(line.strip())
        if not m:
            continue
        phase_id, title = m.group(1), m.group(2)
        found = _docid.scan_plain_field_block(lines, idx + 1)
        raw = {key: value for key, value in found.items() if key in phase_fields}
        if not raw:
            continue  # nothing directly beneath this heading — no phase, not a guess
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


def _slice_child_state(slice_header: Header, corpus: Corpus) -> str | None:
    """One map-plan child's contributed state, per Ruling 72
    (`docs/plans/2026-09-02-w37-field-set-and-rollup-rulings.md`): the slice's *live* leaf
    plan's derived execution — a `PL- kind: leaf` whose `slice:` names it and whose
    `status:` is neither `superseded` nor `retired` — or, when it has none, the slice row's
    own status mapped directly (`draft` -> `not started`, `active` -> `in progress`,
    `closed` -> `closed`). Returns `None` for an *excluded* child: a `retired` slice with
    no live leaf plan. More than one live leaf plan for one slice is "a check 33
    disagreement, not a case to resolve silently" (the ruling's own words) and raises here
    too, rather than picking one.
    """
    if slice_header.id is None:
        raise ValueError("a slice row with no id cannot be a map-plan child")
    norm_slice_id = _normalize_id(slice_header.id)
    live_leaf_plans = [
        r.header
        for r in corpus.records
        if r.header.family == "plan"
        and r.header.kind == "leaf"
        and r.header.slice_ is not None
        and _normalize_id(r.header.slice_) == norm_slice_id
        and r.header.status not in ("superseded", "retired")
    ]
    if len(live_leaf_plans) > 1:
        raise ValueError(
            f"{slice_header.id}: more than one live leaf plan "
            f"({', '.join(p.id or '?' for p in live_leaf_plans)}) — Ruling 72"
        )
    if live_leaf_plans:
        return derive_execution(live_leaf_plans[0], corpus)
    if slice_header.status == "draft":
        return "not started"
    if slice_header.status == "active":
        return "in progress"
    if slice_header.status == "closed":
        return "closed"
    if slice_header.status == "retired":
        return None
    raise ValueError(f"{slice_header.id}: unrecognised slice status {slice_header.status!r}")


def _apply_rollup_precedence(included: list[str]) -> str:
    """Ruling 72's seven-row precedence table over one map plan's non-excluded children,
    already computed (`_slice_child_state`) — split out from `_rollup_map_plan` so the
    table itself, and specifically its "no catch-all" row, is unit-testable against a
    contrived `included` list without needing a corpus that can legitimately produce one
    (every real child state `_slice_child_state` can return is one of `not started`,
    `in progress`, `executed`, `closed`, and every non-empty combination of those four is
    covered by rows 3-7 — the raise below exists as the safety net Ruling 72 requires, not
    because today's inputs can reach it).

    `included` must be non-empty — rows 1 and 2 are `_rollup_map_plan`'s to apply first,
    since they need the *excluded* count too (whether there were no slices at all versus
    every slice being excluded).
    """
    if any(s == "in progress" for s in included):
        return "in progress"  # row 3 (§1.7's own rule)
    if any(s == "not started" for s in included) and any(
        s in ("executed", "closed") for s in included
    ):
        return "in progress"  # row 4
    if all(s == "closed" for s in included):
        return "closed"  # row 5 (§1.7's own rule)
    if all(s in ("closed", "executed") for s in included):
        return "executed"  # row 6
    if all(s == "not started" for s in included):
        return "not started"  # row 7
    raise ValueError(
        f"map-plan roll-up over {included} matches no row of Ruling 72's precedence table"
    )


def _rollup_map_plan(header: Header, corpus: Corpus) -> str:
    """A map plan's roll-up, per Ruling 72
    (`docs/plans/2026-09-02-w37-field-set-and-rollup-rulings.md`) — **not this module's own
    inference**: an earlier version enumerated leaf plans sharing the map plan's `work:`
    directly, which left an unplanned slice invisible to the roll-up, and completed §1.7's
    two stated rules with a catch-all `return "not started"` that silently absorbed every
    combination nobody had enumerated (three confirmed defects, all from that one line).

    The ruled design: children are the map plan's *slices* (`SL-` rows sharing its
    `work:`), each contributing one state via `_slice_child_state`, filtered to the
    non-excluded ones, then matched against `_apply_rollup_precedence`'s explicit seven-row
    table with no catch-all.
    """
    slices = [
        r.header
        for r in corpus.records
        if r.header.family == "slice"
        and r.header.work is not None
        and header.work is not None
        and _normalize_id(r.header.work) == _normalize_id(header.work)
    ]
    if not slices:
        return "not started"  # row 1: no children at all

    states = [_slice_child_state(s, corpus) for s in slices]
    included = [s for s in states if s is not None]

    if not included:
        return "retired"  # row 2: every child excluded, at least one as retired
    return _apply_rollup_precedence(included)


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


# ---------------------------------------------------------------------------------------
# The findings register (Ruling 71, `docs/plans/2026-09-02-w37-field-set-and-rollup-
# rulings.md`) — the phase report's findings element is scoped from here, never from an
# `FD-` essay's header: the essay carries no `phase:`/`work:` (Ruling 70/§1.5's own
# applicability comment) and, after Ruling 70, no `decision:` either. The register row
# carries both, today, before any migration — this reads that row.
# ---------------------------------------------------------------------------------------


@dataclass(frozen=True)
class RegisterRow:
    finding_id: str
    concerns: str
    work_item: str
    phase: str
    decision: str
    status: str  # derived: "closed" | "retired" | "active"
    unowned: bool  # derived


def _register_row_status(decision: str) -> str:
    """`closed` when the Decision cell carries a Resolved annotation (§1.2a: closed covers
    resolved); `retired` when it opens with the `accept` disposition (§1.6: "auditor sets
    closed in place citing the PR; retired for accept"); `active` otherwise.
    """
    lowered = decision.strip().lower()
    if "resolved" in lowered:
        return "closed"
    if lowered.startswith("accept"):
        return "retired"
    return "active"


def _is_unowned(decision: str) -> bool:
    """True for any of the register's own unowned spellings (`unowned`, `unowned by
    design`, `unowned-pending-authorisation`, ...) — the substring `register-lint.py`'s
    own "Unowned-row decay" rule keys off.
    """
    return "unowned" in decision.strip().lower()


def _parse_register(path: Path) -> tuple[list[RegisterRow], int]:
    """Parses `findings/register.md`'s `| Finding id | Concerns | Work item | Phase |
    Decision |` table — the shape `register-lint.py` already parses today, reused rather
    than invented. The header row is found by *position*, never by matching column text
    (the same reason `register-lint.py`'s own parser gives): the first `|---|...|`
    delimiter row marks it, and every `|`-led line after that is data.

    Returns `(parsed rows, data-line count)` **separately** so a caller can assert
    coverage — Ruling 71 acceptance item 2: a malformed row must not silently vanish into
    a smaller-but-plausible count. A row is "parsed" only when it splits into exactly five
    cells; a row that does not still counts toward the data-line total, so the two numbers
    disagree exactly when something did not parse.
    """
    if not path.is_file():
        return [], 0
    lines = path.read_text(encoding="utf-8").splitlines()
    sep_idx = next(
        (i for i, line in enumerate(lines) if re.match(r"^\|\s*-+\s*\|", line.strip())),
        None,
    )
    if sep_idx is None:
        return [], 0
    data_lines = [line for line in lines[sep_idx + 1 :] if line.strip().startswith("|")]
    rows: list[RegisterRow] = []
    for line in data_lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 5:
            continue  # not well-formed — excluded from `rows`, still in `data_lines`
        finding_id, concerns, work_item, phase, decision = cells
        rows.append(
            RegisterRow(
                finding_id=finding_id,
                concerns=concerns,
                work_item=work_item,
                phase=phase,
                decision=decision,
                status=_register_row_status(decision),
                unowned=_is_unowned(decision),
            )
        )
    return rows, len(data_lines)


def _phase_rank(phase: str) -> tuple[int, str]:
    """`"P9" -> (9, "")`, `"P1b" -> (1, "b")` — orders phases the way §1.3 names them
    (`P1b` legacy, no letters from now on), so a carry-in row's phase can be compared
    against the report's target phase as "earlier than", not merely "not equal to".
    """
    m = re.match(r"P(\d+)([a-z]*)$", phase.strip())
    if not m:
        return (2**31, phase)  # unparseable — sorts last; not exercised by this slice's fixtures
    return (int(m.group(1)), m.group(2))


def _findings_figures(rows: list[RegisterRow], phase_id: str) -> tuple[int, int, int, int]:
    """Ruling 71's three phase-scoped figures plus the separately-labelled carry-in:
    `(opened, discharged, unowned_decay, carry_in)`. `opened`/`discharged`/`unowned_decay`
    are computed over rows whose own `Phase` cell equals `phase_id`; `carry_in` is computed
    over every *other* row whose phase sorts earlier, regardless of which phase entered
    this call — an unowned row does not stop decaying just because two phases have passed.
    """
    target_rank = _phase_rank(phase_id)
    in_phase = [r for r in rows if r.phase == phase_id]
    opened = len(in_phase)
    discharged = sum(1 for r in in_phase if r.status in ("closed", "retired"))
    unowned_decay = sum(1 for r in in_phase if r.status == "active" and r.unowned)
    carry_in = sum(
        1
        for r in rows
        if r.phase != phase_id
        and _phase_rank(r.phase) < target_rank
        and r.status == "active"
        and r.unowned
    )
    return opened, discharged, unowned_decay, carry_in


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

    # 5. Findings opened versus discharged, with the unowned-decay count — scoped from
    # `findings/register.md`, per Ruling 71 (docs/plans/2026-09-02-w37-field-set-and-
    # rollup-rulings.md): the note was not silent on this, §5.2 and §5.4 name the register
    # as the carrier. A parse-coverage mismatch raises rather than silently under-counting
    # (Ruling 71 acceptance item 2).
    register_rows, register_data_lines = _parse_register(root / "findings" / "register.md")
    if len(register_rows) != register_data_lines:
        raise ValueError(
            f"findings/register.md: parsed {len(register_rows)} of {register_data_lines} "
            "data row(s) — coverage mismatch (Ruling 71 acceptance item 2)"
        )
    opened, discharged, unowned_decay, carry_in = _findings_figures(register_rows, phase_id)
    lines.append(
        f"5. Findings opened versus discharged, from the register: {opened} opened in "
        f"{phase_id}, {discharged} discharged, {unowned_decay} unowned-decay in "
        f"{phase_id}, plus {carry_in} unowned-decay carried in from an earlier phase"
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
        if not index_path.is_file():
            if not corpus.records:
                # Found while wiring `--check` into `.github/workflows/docs.yml` as a gate
                # step (W37-4): pre-migration, `docs/INDEX.md` does not exist and nothing
                # does — treating "absent" as "stale" unconditionally would red this step
                # on every run until W37-6, for a file only the migration creates. Mirrors
                # the default (write) action's own "cannot be run against the live corpus
                # until W37-6" refusal below: zero records is the pre-migration state, not
                # drift, so there is nothing to be stale against.
                print(
                    f"{index_path} does not exist and zero governed records were found "
                    f"under {args.root} — nothing to check yet (pre-migration)"
                )
                return 0
            print(
                f"{index_path} does not exist, but {len(corpus.records)} governed "
                "record(s) were found — run `python3 scripts/doc-index.py` to create it"
            )
            return 1
        current = index_path.read_text(encoding="utf-8")
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
