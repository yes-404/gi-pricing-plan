"""`docs/_templates/*.md` against `scripts/_docid.py`'s `parse_header` — the integration
neither W37-1 (the templates, `docs/plans/2026-08-31-...`) nor W37-2 (the parser,
`tests/test_doc_id.py`) covers alone: does a template, filled in the way its own leading
comment instructs an author to fill it, actually parse?

Ten document-family templates (`ADR`, `CR`, `FD`, `LG`, `PL`, `REFERENCE`, `RFC`, `RL`,
`RS`, `WF`) carry `---`-delimited YAML front matter and must parse — once an author strips
the template's own leading `<!-- ... -->` comment and fills in the placeholders, exactly
the sequence every template's own comment instructs ("Fill in every placeholder, delete
this comment block"). Three (`WK`, `SL`, `PHASE`) carry no top-level `---` block *by
design*: NT-0019 (`docs/notes/0019-one-id-per-document.md`) §1.5 puts a `WK-`/`SL-` header
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
import sys
import types
from typing import Any

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCID_MODULE_PATH = ROOT / "scripts" / "_docid.py"
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
# WK.md / SL.md: no top-level `---` by design (NT-0019 §1.5) — the header is a fenced
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

    # Signal 2: the fenced block itself — the actual header content, per NT-0019
    # §1.5's "as a fenced block under the row's heading" — is well-formed against the
    # same closed grammar and carries the right family, wrapped in the `---`
    # delimiters the grammar (as opposed to the fence) expects.
    fenced_body = _extract_fenced_yaml_block(rendered)
    wrapped = f"---\n{fenced_body}\n---\n"
    fenced_header = _write_and_parse(docid, tmp_path, "fenced-SL.md", wrapped)
    assert fenced_header is not None, f"SL.md: fenced block failed to parse: {fenced_body!r}"
    assert fenced_header.family == "slice"


def test_wk_template_has_no_top_level_front_matter(
    docid: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """WK.md, the same two signals as SL.md above — but only the first one holds.

    `WK.md`'s fenced block itself currently carries the *same class* of defect this
    PR fixes in FD.md/REFERENCE.md/RFC.md: its `owner:` field's inline comment wraps
    onto a second, indented physical line —

        owner: maintainer                # opens (draft); planner writes the map plan; maintainer
                                          # sets active; maintainer accepts the close

    — which `_parse_front_matter_body` rejects as an indented continuation line
    (NT-0019 §1.5's closed, flat grammar has no continuation-line concept), exactly
    as it rejected REFERENCE.md's old `owner:` comment before this fix. Nothing in
    this repository parses a `WK-`/`SL-` row's fenced content today
    (`doc-id.py scan_roadmap_row_ids` reads only the heading line's id via regex, never
    the block body), so this is not yet a live break — but it is real, and it is the
    same defect class.

    This PR's authorized scope is `FD.md`, `REFERENCE.md` and `RFC.md` only — the lead
    was explicit that `WK.md` "correctly has no `---` front matter" and must not be
    altered here. So this test does not fix WK.md and does not assert its fenced block
    parses; it pins *today's* actual behaviour (`HeaderError`, not a silent pass) so
    the finding is visible in the suite rather than only in a chat transcript, and
    reported to the lead separately as new information outside this PR's scope. If
    `WK.md` is fixed in a future PR, this assertion starts failing — correctly: update
    it there, the same way REFERENCE.md's fenced-analogue was fixed here.
    """
    raw = (TEMPLATES_DIR / "WK.md").read_text(encoding="utf-8")
    rendered = _render_as_author_would(raw)

    whole_file_header = _write_and_parse(docid, tmp_path, "WK.md", rendered)
    assert whole_file_header is None
    assert not rendered.lstrip("\n").startswith("---")

    fenced_body = _extract_fenced_yaml_block(rendered)
    wrapped = f"---\n{fenced_body}\n---\n"
    with pytest.raises(docid.HeaderError, match="indented line"):
        _write_and_parse(docid, tmp_path, "fenced-WK.md", wrapped)


# -----------------------------------------------------------------------------------
# PHASE.md: outside the id standard entirely (NT-0019 §1.1 rule 4) — plain fields
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
# second, indented physical line inside a `---` block breaks parsing (NT-0019 §1.5's
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
