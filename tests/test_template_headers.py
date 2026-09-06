"""`docs/_templates/*.md` against `scripts/_docid.py`'s `parse_header` — the integration
neither W37-1 (the templates, `docs/plans/2026-08-31-...`) nor W37-2 (the parser,
`tests/test_doc_id.py`) covers alone: does a template, filled in the way its own leading
comment instructs an author to fill it, actually parse?

Ten document-family templates (`ADR`, `CR`, `FD`, `LG`, `PL`, `REFERENCE`, `RFC`, `RL`,
`RS`, `WF`) carry `---`-delimited YAML front matter and must parse — once an author strips
the template's own leading `<!-- ... -->` comment and fills in the placeholders, exactly
the sequence every template's own comment instructs ("Fill in every placeholder, delete
this comment block"). Three (`WK`, `SL`, `PHASE`) carry no top-level `---` block *by
design*: RFC-937 (`docs/rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md`) §1.5 puts a `WK-`/`SL-` header
in a fenced ```yaml block under the row's own heading rather than the file's own front
matter, and §1.1 rule 4 puts a phase outside the id standard entirely. Neither is a defect,
and this suite must not mistake the one for the other.

A first attempt at this check was vacuous: `parse_header` on the *raw* template (leading
comment intact) sees a first line that is not exactly `---` and returns `None` for all
thirteen files alike — the same `None` a fully broken template would also produce. Every
test below strips the comment and fills placeholders first, so a `None` means what it
should; and the three fenced/plain families get their own assertion of *why* they return
`None` (the fenced block is extracted and parsed on its own terms; the plain-field block is
confirmed to carry no closed-grammar block at all) rather than being waved through by the
same falsy check that would also pass on total garbage.

No `@pytest.mark.req` marker: like `tests/test_doc_id.py` (whose reasoning this repeats),
this is correctness of the templates against the parser, not evidence for a numbered
platform requirement.
"""

from __future__ import annotations

import importlib.util
import pathlib
import re
import shutil
import sys
import types
from datetime import date
from typing import Any

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCID_MODULE_PATH = ROOT / "scripts" / "_docid.py"
DOC_ID_MODULE_PATH = ROOT / "scripts" / "doc-id.py"
TEMPLATES_DIR = ROOT / "docs" / "_templates"

if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))


def _load_by_path(name: str, path: pathlib.Path) -> types.ModuleType:
    """Load `scripts/_docid.py` by path.

    Mirrors `tests/test_doc_id.py`'s helper of the same purpose, duplicated rather than
    imported so this file stays runnable standalone
    (`uv run pytest tests/test_template_headers.py`) with no import-order dependency on
    that file. Loading by name (`import _docid`) after the `sys.path` insert above would
    also resolve, since `_docid` (unlike the hyphenated `doc-id.py`) is a legal module
    identifier — but by-path loading is what the sibling test file does, and it costs
    nothing to read the same way twice.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def docid() -> types.ModuleType:
    return _load_by_path("_docid", DOCID_MODULE_PATH)


# -----------------------------------------------------------------------------------
# Simulating "an author fills in the template": strip the leading `<!-- ... -->`
# comment block (every template's own first instruction), then fill placeholders.
# -----------------------------------------------------------------------------------

_LEADING_COMMENT_RE = re.compile(r"\A<!--.*?-->\n?\n?", re.DOTALL)

# Deliberately does NOT match across a newline (`\n` is excluded from the character
# class). A `<...>` placeholder that spans two physical lines — the exact defect fixed
# in FD.md and RFC.md — leaves its second, indented line untouched by this
# substitution, so a future re-wrap reproduces the same `HeaderError` this suite
# catches today; see `test_a_wrapped_bracket_placeholder_breaks_parsing` below for the
# mechanism, proven directly on synthetic input.
_BRACKET_PLACEHOLDER_RE = re.compile(r"<[^<>\n]*>")


def _strip_leading_comment(text: str) -> str:
    return _LEADING_COMMENT_RE.sub("", text, count=1)


def _fill_placeholders(text: str) -> str:
    """Fill every placeholder a template author is instructed to fill in, the way an
    author who follows the templates literally would: pad-number and date tokens get a
    realistic value, `P<n>` becomes a real phase, and any remaining single-line `<...>`
    bracket gets a filler string. Never touches a `#` comment — an author who keeps a
    template's explanatory comments, exactly as REFERENCE.md's own header used to
    invite before this fix, is exactly the case the fix must survive.
    """
    text = text.replace("NNNNN", "01234")
    text = text.replace("YYYY-MM-DD", "2026-09-02")
    text = text.replace("P<n>", "P2")
    return _BRACKET_PLACEHOLDER_RE.sub("filled placeholder", text)


def _render_as_author_would(raw_text: str) -> str:
    return _fill_placeholders(_strip_leading_comment(raw_text))


def _write_and_parse(
    docid: types.ModuleType, tmp_path: pathlib.Path, name: str, content: str
) -> Any:
    # `Any`, not `Header | None`: `docid` is loaded dynamically (`types.ModuleType`), so
    # mypy cannot see through to `_docid.py`'s real return type here — the same shape
    # `tests/test_doc_id.py` accepts by calling `docid.parse_header(...)` inline rather
    # than through a wrapper. `pyproject.toml`'s `disallow_any_explicit = false` permits
    # stating that plainly instead of a `# type: ignore` at every call site below.
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return docid.parse_header(path)


# -----------------------------------------------------------------------------------
# The ten document families: `---`-delimited front matter, must parse and carry the
# right `family` once rendered the way an author renders them. Reads the real
# templates off disk, so a future re-wrap in any of these ten fails this test the same
# way it failed on FD.md, REFERENCE.md and RFC.md before this fix.
# -----------------------------------------------------------------------------------

_DOCUMENT_FAMILIES = [
    ("ADR.md", "decision"),
    ("CR.md", "closure"),
    ("FD.md", "finding"),
    ("LG.md", "ledger"),
    ("PL.md", "plan"),
    ("REFERENCE.md", "reference"),
    ("RFC.md", "proposal"),
    ("RL.md", "ruling"),
    ("RS.md", "research"),
    ("WF.md", "workflow"),
]


@pytest.mark.parametrize(("filename", "expected_family"), _DOCUMENT_FAMILIES)
def test_document_template_parses_to_its_family_once_filled_in(
    docid: types.ModuleType,
    tmp_path: pathlib.Path,
    filename: str,
    expected_family: str,
) -> None:
    raw = (TEMPLATES_DIR / filename).read_text(encoding="utf-8")
    rendered = _render_as_author_would(raw)
    header = _write_and_parse(docid, tmp_path, filename, rendered)
    assert header is not None, (
        f"{filename}: parse_header returned None on filled-in content — either no "
        f"`---` block survived rendering, or the leading-comment strip did not work"
    )
    assert header.family == expected_family


# -----------------------------------------------------------------------------------
# WK.md / SL.md: no top-level `---` by design (RFC-937 §1.5) — the header is a fenced
# ```yaml block under the row's own heading. The whole-file `None` is checked
# alongside the fenced block's own content so a `None` here reads as "fenced, as
# designed" rather than "broken, and silently waved through" — the same distinction
# `_render_as_author_would` draws for the ten document families above.
# -----------------------------------------------------------------------------------

_FENCE_RE = re.compile(r"```yaml\n(.*?)\n```", re.DOTALL)


def _extract_fenced_yaml_block(text: str) -> str:
    match = _FENCE_RE.search(text)
    assert match is not None, "no ```yaml fenced block found"
    return match.group(1)


def test_sl_template_has_no_top_level_front_matter_but_its_fenced_block_parses(
    docid: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    raw = (TEMPLATES_DIR / "SL.md").read_text(encoding="utf-8")
    rendered = _render_as_author_would(raw)

    # Signal 1: the file itself does not start with `---` — parse_header returns None
    # for the *designed* reason (no top-level block), not because parsing broke
    # midway through a block that is actually there.
    whole_file_header = _write_and_parse(docid, tmp_path, "SL.md", rendered)
    assert whole_file_header is None
    assert not rendered.lstrip("\n").startswith("---")

    # Signal 2: the fenced block itself — the actual header content, per RFC-937
    # §1.5's "as a fenced block under the row's heading" — is well-formed against the
    # same closed grammar and carries the right family, wrapped in the `---`
    # delimiters the grammar (as opposed to the fence) expects.
    fenced_body = _extract_fenced_yaml_block(rendered)
    wrapped = f"---\n{fenced_body}\n---\n"
    fenced_header = _write_and_parse(docid, tmp_path, "fenced-SL.md", wrapped)
    assert fenced_header is not None, f"SL.md: fenced block failed to parse: {fenced_body!r}"
    assert fenced_header.family == "slice"


def test_wk_template_has_no_top_level_front_matter_but_its_fenced_block_parses(
    docid: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """WK.md, the same two signals as SL.md above — fixed 2026-09-02 (W37-4,
    `docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md`), deliberately, not by
    loosening this test.

    Until this fix, `WK.md`'s fenced block carried the *same class* of defect #570 fixed
    in FD.md/REFERENCE.md/RFC.md: its `owner:` field's inline comment wrapped onto a
    second, indented physical line, which `_parse_front_matter_body` rejects as an
    indented continuation line (RFC-937 §1.5's closed, flat grammar has no
    continuation-line concept). #570's own scope was `FD.md`/`REFERENCE.md`/`RFC.md`
    only, and it left WK.md's copy of the defect in place on purpose, pinning
    `HeaderError` here so the finding stayed visible in the suite rather than only in a
    chat transcript — with an explicit instruction that fixing WK.md must update this
    assertion, not merely re-pass it. §1.5's fenced-block policy (row families, under a
    heading) is what W37-4 enforces, so the template and its own test move together in
    the same commit that does the enforcing, the same relationship #570 already set for
    the ten `---`-block families.
    """
    raw = (TEMPLATES_DIR / "WK.md").read_text(encoding="utf-8")
    rendered = _render_as_author_would(raw)

    # Signal 1: the file itself does not start with `---` — parse_header returns None
    # for the *designed* reason (no top-level block), not because parsing broke midway
    # through a block that is actually there.
    whole_file_header = _write_and_parse(docid, tmp_path, "WK.md", rendered)
    assert whole_file_header is None
    assert not rendered.lstrip("\n").startswith("---")

    # Signal 2: the fenced block itself now parses cleanly, carrying the right family.
    fenced_body = _extract_fenced_yaml_block(rendered)
    wrapped = f"---\n{fenced_body}\n---\n"
    fenced_header = _write_and_parse(docid, tmp_path, "fenced-WK.md", wrapped)
    assert fenced_header is not None, f"WK.md: fenced block failed to parse: {fenced_body!r}"
    assert fenced_header.family == "work"


# -----------------------------------------------------------------------------------
# PHASE.md: outside the id standard entirely (RFC-937 §1.1 rule 4) — plain fields
# under a heading, not YAML front matter, no `id:`, no `family:`, no fenced block
# either.
# -----------------------------------------------------------------------------------


def test_phase_template_has_no_front_matter_block_of_any_kind(
    docid: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    raw = (TEMPLATES_DIR / "PHASE.md").read_text(encoding="utf-8")
    rendered = _render_as_author_would(raw)

    header = _write_and_parse(docid, tmp_path, "PHASE.md", rendered)
    assert header is None

    # Distinguishes "correctly has nothing to parse" from "something is there and was
    # silently skipped": no `---` line and no ```yaml fence anywhere in the rendered
    # template — there is no closed-grammar block at all, fenced or otherwise.
    lines = rendered.splitlines()
    assert "---" not in lines
    assert "```yaml" not in rendered
    assert "id:" not in rendered
    assert "family:" not in rendered


# -----------------------------------------------------------------------------------
# The full sweep: every template under docs/_templates/ is accounted for by exactly
# one of the two shapes above. A 14th template dropped in later without a matching
# entry here fails this test by name, rather than being silently uncovered.
# -----------------------------------------------------------------------------------


def test_every_template_on_disk_is_covered_by_the_document_or_row_phase_partition() -> None:
    on_disk = {p.name for p in TEMPLATES_DIR.glob("*.md")}
    accounted_for = {name for name, _ in _DOCUMENT_FAMILIES} | {"WK.md", "SL.md", "PHASE.md"}
    assert on_disk == accounted_for


# -----------------------------------------------------------------------------------
# Broken-input proof: a `#` comment or a `<...>` placeholder that wraps onto a
# second, indented physical line inside a `---` block breaks parsing (RFC-937 §1.5's
# closed, flat grammar has no continuation-line concept) — this is the exact defect
# fixed in REFERENCE.md, FD.md and RFC.md. Proven directly here on synthetic content
# mirroring each file's pre-fix shape, so the mechanism is caught even if a future
# edit changes all three real templates enough that they no longer serve as their own
# regression fixture.
# -----------------------------------------------------------------------------------


def test_a_wrapped_inline_comment_breaks_parsing(
    docid: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    # REFERENCE.md's shape before this fix: a `#` comment explaining `owner:` that
    # wraps onto further indented lines instead of staying on `owner:`'s own line.
    broken = (
        "---\n"
        "family: reference\n"
        "title: t\n"
        "status: active\n"
        "created: 2026-09-02\n"
        "owner: maintainer                # amendments to process/ arrive as RFC- + RL-;\n"
        "                                  # continuing on an indented second line\n"
        "corrected_by: []\n"
        "relates: []\n"
        "---\n"
    )
    with pytest.raises(docid.HeaderError, match="indented line"):
        _write_and_parse(docid, tmp_path, "broken-reference.md", broken)


def test_a_wrapped_bracket_placeholder_breaks_parsing(
    docid: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    # FD.md's `decision:` shape before this fix: a `<...>` placeholder spanning two
    # physical lines, the second one indented.
    broken = (
        "---\n"
        "id: FD-00001\n"
        "family: finding\n"
        "title: t\n"
        "status: active\n"
        "created: 2026-09-02\n"
        "owner: auditor\n"
        "tree: abc1234\n"
        "decision: <fix before close | accept | carry forward, with qualifiers —\n"
        "  the register disposition; never confused with `status:`>\n"
        "corrected_by: []\n"
        "relates: []\n"
        "---\n"
    )
    with pytest.raises(docid.HeaderError, match="indented line"):
        _write_and_parse(docid, tmp_path, "broken-fd.md", broken)


# -----------------------------------------------------------------------------------
# Rulings 79 and 80 (docs/rulings/INDEX.md#2026-09-02-w37-template-parser-conflicts-rulingsmd):
# `WK.md`/`SL.md`/`PHASE.md` against the parser that actually consumes a *row* or a
# *phase section* embedded mid-`roadmap.md` — `scripts/doc-index.py`'s
# `scan_roadmap_rows`/`scan_phase_sections` — never exercised above, which only proves
# these templates against `_docid.py`'s file-level `parse_header` (RL-998 §1's own
# finding: "It exercises a different parser from the one that consumes a row, and
# passes."). Extended here rather than in a new file, per RL-998 §4: "a second file
# would repeat the near-miss rather than close it."
# -----------------------------------------------------------------------------------

DOC_INDEX_MODULE_PATH = ROOT / "scripts" / "doc-index.py"


@pytest.fixture
def doc_index() -> types.ModuleType:
    """Function-scoped, deliberately not `module` like `docid` above: several tests below
    `setattr` the loaded module's own `_TEMPLATES_DIR`, and a shared module instance would
    leak that mutation into whichever test happens to run next. Reloading fresh per test
    is the same fix `tests/test_audit_docs_ids.py`'s own `audit` fixture already uses for
    the identical hazard against `scripts/audit-docs.py`'s `_TEMPLATES_DIR`.
    """
    return _load_by_path("_doc_index_for_template_headers", DOC_INDEX_MODULE_PATH)


def _row_fixture(fenced_body: str) -> str:
    """A `roadmap.md` carrying exactly one row: `fenced_body` (already rendered/filled)
    under a bare `###` heading. `scan_roadmap_rows` only cares that the nearest preceding
    heading is level 3 or deeper — the heading's own text is never parsed — so a row
    template's real heading is not needed here.
    """
    return f"# Roadmap (fixture)\n\n### row under test\n\n```yaml\n{fenced_body}\n```\n"


@pytest.mark.parametrize(
    ("template_filename", "family"),
    [("WK.md", "work"), ("SL.md", "slice")],
)
def test_row_template_fenced_block_parses_through_doc_index_row_parser(
    doc_index: types.ModuleType,
    tmp_path: pathlib.Path,
    template_filename: str,
    family: str,
) -> None:
    """RL-998 §4's positive control: "a check that copies each row template's fenced
    block into a roadmap fixture and parses it with doc-index.py's row parser. It must
    fail today, before the fix, with `unknown row field 'tree'`." `WK.md` and `SL.md` both
    declare `tree:`, `corrected_by:` and `relates:`; the old `_ROW_FIELDS` rejected all
    three. After the fix, the row parses and the three fields are actually wired (§3 item
    3) rather than hardcoded away in `_row_header_from_raw`.
    """
    raw = (TEMPLATES_DIR / template_filename).read_text(encoding="utf-8")
    rendered = _render_as_author_would(raw)
    fenced_body = _extract_fenced_yaml_block(rendered)
    roadmap = tmp_path / "roadmap.md"
    roadmap.write_text(_row_fixture(fenced_body), encoding="utf-8")

    records = doc_index.scan_roadmap_rows(roadmap)

    assert len(records) == 1, records
    header = records[0].header
    assert header.family == family
    assert header.tree == "filled placeholder"
    assert header.corrected_by == ()
    assert header.relates == ()


def test_kind_field_on_a_work_row_is_rejected(
    doc_index: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """RL-998 §4: "a check that `kind:` on a `WK-` row is rejected. This is the half a
    fields-added fix leaves behind, and it must red." `docs/_templates/WK.md`'s own
    comment forbids `kind:` by name; the old `_ROW_FIELDS` wrongly admitted it (RL-998
    §1: "wrong in both directions at once").
    """
    roadmap = tmp_path / "roadmap.md"
    roadmap.write_text(
        _row_fixture(
            "id: WK-00001\nfamily: work\ntitle: t\nstatus: draft\nkind: something"
        ),
        encoding="utf-8",
    )
    with pytest.raises(doc_index.HeaderError, match="kind"):
        doc_index.scan_roadmap_rows(roadmap)


def test_row_field_policy_changes_with_the_wk_template(
    doc_index: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """RL-981 §4 item 2, applied to `doc-index.py` per RL-998 §4: "add a key to
    WK.md and a row using it parses; remove a key and the same row is rejected ...  the
    signature of a policy transcribed." Proven on a *copy* of the real templates (never
    the real `docs/_templates/`, which this test must not mutate), by redirecting
    `doc_index._TEMPLATES_DIR` — the same `setattr` idiom
    `tests/test_audit_docs_ids.py::test_check_30_field_policy_changes_with_the_template`
    already uses for `audit-docs.py`'s own constant of the same name.
    """
    templates_copy = tmp_path / "templates"
    shutil.copytree(TEMPLATES_DIR, templates_copy)
    setattr(doc_index, "_TEMPLATES_DIR", templates_copy)  # noqa: B010 -- mypy needs setattr here

    wk = templates_copy / "WK.md"
    text = wk.read_text(encoding="utf-8")
    assert "owner: maintainer" in text, "fixture assumption: WK.md's owner: line changed"
    assert "relates: []" in text, "fixture assumption: WK.md's relates: line changed"

    roadmap = tmp_path / "roadmap.md"
    roadmap.write_text(
        _row_fixture(
            "id: WK-00001\nfamily: work\ntitle: t\nstatus: draft\nowner: maintainer"
        ),
        encoding="utf-8",
    )

    # Remove a key the template declares today (`owner:`): the same row is rejected.
    without_owner = "\n".join(
        line for line in text.splitlines() if not line.strip().startswith("owner:")
    )
    wk.write_text(without_owner, encoding="utf-8")
    with pytest.raises(doc_index.HeaderError, match="owner"):
        doc_index.scan_roadmap_rows(roadmap)

    # Add a key the template does not declare: a row using it now parses.
    widened = text.replace("relates: []", "relates: []\nextra_test_field: x")
    wk.write_text(widened, encoding="utf-8")
    roadmap.write_text(
        _row_fixture(
            "id: WK-00001\nfamily: work\ntitle: t\nstatus: draft\n"
            "owner: maintainer\nextra_test_field: x"
        ),
        encoding="utf-8",
    )
    records = doc_index.scan_roadmap_rows(roadmap)
    assert len(records) == 1, (
        "adding a key to WK.md did not widen doc-index.py's row parser — the policy is "
        "not actually being read from the template"
    )


def test_phase_template_body_parses_via_scan_phase_sections(
    doc_index: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """RL-999 §4's positive control: "PHASE.md's own body, placeholders filled, parsed
    by scan_phase_sections, must yield the phase it describes. It must fail today, before
    the fix." Today `scan_phase_sections` only ever reads the first *fenced* block below a
    phase heading; `PHASE.md`'s own body carries none (`_EXPECTED_NO_BLOCK_TEMPLATES` in
    `audit-docs.py` already enforces this by path), so the old code finds nothing at all
    for a pristine phase section — `sections == []` — the "finds nothing" half of the
    defect; `test_phase_section_with_no_fields_of_its_own_never_borrows_a_later_blocks_
    fields` below proves the other half, the "borrows a later block" misattribution
    PROBE 2 in the ruling actually hit (which needs a Work fenced block present to borrow
    from — this fixture, being just PHASE.md's own body, has none).
    """
    raw = (TEMPLATES_DIR / "PHASE.md").read_text(encoding="utf-8")
    rendered = _render_as_author_would(raw)
    roadmap = tmp_path / "roadmap.md"
    roadmap.write_text(rendered, encoding="utf-8")

    sections = doc_index.scan_phase_sections(roadmap)

    assert len(sections) == 1, sections
    section = sections[0]
    assert section.phase == "P2"
    assert section.status == "draft"
    assert section.works == ("WK-01234", "WK-01234")


def test_phase_section_with_no_fields_of_its_own_never_borrows_a_later_blocks_fields(
    doc_index: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """RL-999 §4 item 2, PROBE 2's own shape reproduced directly: a phase heading with
    nothing of its own directly beneath it, followed by a `WK-` row whose `status:`
    deliberately differs from any real phase status. Before the fix,
    `scan_phase_sections`'s unbounded lookahead (`rest = "\n".join(lines[idx + 1:])`)
    finds the Work's fenced block, reads its `status: retired` as the *phase's* status,
    and reports no attached works at all — PROBE 2's exact result. After the fix: "a phase
    section carrying no fields must produce no phase, or a loud failure — never a phase
    built from a later block."
    """
    roadmap = tmp_path / "roadmap.md"
    roadmap.write_text(
        "# Roadmap (fixture)\n\n"
        "## P2 — Rating engine live\n\n"
        "### WK-01201 — Some work\n\n"
        "```yaml\n"
        "id: WK-01201\n"
        "family: work\n"
        "title: Some work\n"
        "status: retired\n"
        "```\n",
        encoding="utf-8",
    )

    sections = doc_index.scan_phase_sections(roadmap)

    assert sections == [], (
        f"a phase heading with nothing directly beneath it must yield no phase at all, "
        f"never one built from a later heading's block: got {sections!r}"
    )


def test_phase_section_fields_change_with_the_phase_template(
    doc_index: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """RL-999 §4 item 3, RL-981 §4 item 2's mutation applied to `PHASE.md`: "rename
    works: in the template and a phase section using the old name stops being read."
    Proven on a *copy* of the real templates, never the real `docs/_templates/`.
    """
    templates_copy = tmp_path / "templates"
    shutil.copytree(TEMPLATES_DIR, templates_copy)
    phase_template = templates_copy / "PHASE.md"
    text = phase_template.read_text(encoding="utf-8")
    assert "works: WK-NNNNN, WK-NNNNN" in text, (
        "fixture assumption: PHASE.md's works: line changed"
    )
    phase_template.write_text(text.replace("works:", "renamed_field:"), encoding="utf-8")
    setattr(doc_index, "_TEMPLATES_DIR", templates_copy)  # noqa: B010 -- mypy needs setattr here

    roadmap = tmp_path / "roadmap.md"
    roadmap.write_text(
        "# Roadmap (fixture)\n\n## P2 — Some phase\nstatus: active\nworks: WK-00001\n",
        encoding="utf-8",
    )

    sections = doc_index.scan_phase_sections(roadmap)

    assert len(sections) == 1, sections
    assert sections[0].works == (), (
        "renaming works: in PHASE.md did not change what scan_phase_sections reads — "
        "the field set is not actually derived from the template"
    )


def test_restructure_roadmap_writer_round_trips_through_doc_index_readers(
    doc_index: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """RL-977 (`docs/rulings/RL-00977-the-fix-is-inert-on-the-real-corpus-so-the-
    boundary-is-free-it-lands-on-its-own-and-the-reader-and-the-writer-land-together.md`) §4: "take migrate's emitted row block and phase section, feed each to
    scan_roadmap_rows and scan_phase_sections, and require the fields to survive ... This
    must be a test in the branch that lands the fix, not a task carried into W37-6."

    Exercises `doc-id.py`'s `_restructure_roadmap` — the writer half of Rulings 79 §3 item
    4 and 80 §3 item 4 — directly against `doc-index.py`'s own readers, rather than through
    the full `migrate()` pipeline (`tests/test_doc_id_migrate.py::
    test_roadmap_restructure_is_readable_by_doc_index` already covers that end to end; this
    is the narrower, Ruling-81-cited proof that the writer and reader this branch changes
    together still agree). RL-977 §2's rejected option — "fix the reader and leave the
    writer ... migrate emits blocks its own reader rejects" — is exactly the failure this
    would catch: a `HeaderError` here means the split happened.

    Rulings 90-92 (`docs/rulings/INDEX.md#2026-09-02-w37-roadmap-transform-rulingsmd`) turned
    `_restructure_roadmap` from a function that *created* `docs/roadmap.md` (a stub built
    only from its draft arguments) into one that edits an *existing* file in place,
    surgically — removing exactly the leading rows its drafts supersede and leaving
    everything else untouched (RL-992 obligation 3). This fixture writes that existing
    file itself, with a real leading row for `WK-657` and trailing narrative after it, so the
    round-trip below exercises the in-place edit the writer actually performs now, and
    the final assertion — that the trailing narrative survives — is what would have caught
    the writer regressing back to a full overwrite (this file's own fixture used to rely
    on that overwrite to conjure `docs/roadmap.md` out of nothing, which is the defect
    RL-992 exists to remove).
    """
    doc_id_cli = _load_by_path("_doc_id_for_template_headers", DOC_ID_MODULE_PATH)

    root = tmp_path
    templates_copy = root / "docs" / "_templates"
    shutil.copytree(TEMPLATES_DIR, templates_copy)

    docs_dir = root / "docs"
    docs_dir.mkdir(exist_ok=True)
    trailing_narrative = "Trailing narrative that must survive the in-place edit untouched."
    (docs_dir / "roadmap.md").write_text(
        "# Roadmap (fixture)\n\n"
        "## Phase 2 — Rating Engine\n\n"
        "| WS | Scope | Status |\n"
        "|---|---|---|\n"
        "| **WK-657** | Existing workstream, superseded by this restructure | active |\n\n"
        f"{trailing_narrative}\n",
        encoding="utf-8",
    )

    work = doc_id_cli._Draft(
        materialize="roadmap_row", prefix="WK", kind=None, title="Round-trip work",
        status="active", created=date(2026, 9, 2), owner="maintainer",
        tie_break=("roadmap.md", 0), old_token="WK-657", phase="P2", number=1,
    )
    slice_ = doc_id_cli._Draft(
        materialize="roadmap_row", prefix="SL", kind=None, title="Round-trip slice",
        status="draft", created=date(2026, 9, 2), owner="planner",
        tie_break=("roadmap.md", 1), old_token="W1-1", phase="P2", number=1,
        work_token="WK-657",
    )
    occurrences = doc_id_cli._scan_roadmap_rows(
        (docs_dir / "roadmap.md").read_text(encoding="utf-8")
    )
    doc_id_cli._restructure_roadmap(root, [work, slice_], {"2": "Round-trip phase"}, occurrences)

    roadmap = root / "docs" / "roadmap.md"
    restructured = roadmap.read_text(encoding="utf-8")
    assert trailing_narrative in restructured, (
        "content placed after the superseded row did not survive the in-place edit -- "
        "this is the assertion that would have caught a regression back to the old "
        "full-file overwrite"
    )
    assert "Existing workstream, superseded by this restructure" not in restructured, (
        "the row this draft supersedes should have been removed, not left duplicated "
        "alongside the new WK- block"
    )

    rows = doc_index.scan_roadmap_rows(roadmap)
    assert {r.header.id for r in rows} == {"WK-1", "SL-1"}, rows
    slice_header = next(r.header for r in rows if r.header.id == "SL-1")
    assert slice_header.work == "WK-1"

    sections = doc_index.scan_phase_sections(roadmap)
    assert len(sections) == 1, sections
    assert sections[0].phase == "P2"
    assert sections[0].works == ("WK-1",)
