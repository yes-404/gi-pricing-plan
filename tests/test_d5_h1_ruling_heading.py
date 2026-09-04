"""Row (d5): a ruling heading is discovered at H1 as well as at H2.

`_RULING_HEADING_RE` matched `^##` only, so the H1-only ruling files (Rulings 59/60/61)
were never discovered by `_discover_multi_ruling_files` and therefore never rewritten —
which is what held row (d5) at FAIL. The regex now accepts `^#{1,2}`.

No `@pytest.mark.req` marker: this is correctness of the id-migration tool itself, not
evidence for a numbered requirement — the same reading `tests/test_doc_id.py` and
`tests/test_audit_docs_ids.py` record for their own modules.
"""

import importlib.util
import pathlib
import sys
import types
from typing import Final

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOC_ID_SCRIPT_PATH = ROOT / "scripts" / "doc-id.py"

# Every ruling heading below is BUILT from `_R` plus a number, never spelled out as a
# citation, and that is load-bearing twice over. Row (d5)'s predicate greps for that
# spelled-out form over `git ls-files --cached --others`, so this file is part of the very
# corpus it tests. Spelled out, the fixture number below would be a citation of a ruling
# that does not exist, which no migration can ever rewrite: it holds (d5) at FAIL for as
# long as this file is tracked, and measurement showed three such lines were (d5)'s entire
# residue. The real numbers are worse the other way — those rulings DO have records, so the
# migration would rewrite them to `RL-` ids and silently break the assertions underneath.
# Building the token from a name and an int leaves this file inert to both, and note that
# this comment must observe its own rule: writing the bad example out to explain it would
# reintroduce exactly the citation it warns about.
_R: Final = "Ruling"
_H1_NUMBER: Final = 59
_H2_NUMBER: Final = 60
_DEEP_NUMBER: Final = 61
#: Deliberately outside the real ruling range: the fixture must not collide with a record.
_FIXTURE_NUMBER: Final = 999

# `scripts/` is not a package and is not on `sys.path` by default, but `doc-id.py` does
# `import _docid` at its own top level. A `python3 scripts/doc-id.py` run gets this for
# free (Python puts the script's own directory on `sys.path[0]`); a
# `spec_from_file_location` load does not. Same note as `tests/test_doc_id.py`.
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))


def _load_by_path(name: str, path: pathlib.Path) -> types.ModuleType:
    """Load a hyphenated `scripts/` module by path — `doc-id.py` cannot be `import`ed by
    name. Same idiom `tests/test_doc_id.py` and `tests/test_audit_docs_ids.py` use.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_h1_ruling_heading_is_discovered(tmp_path: pathlib.Path) -> None:
    """An H1 ruling heading is discovered and allocated the `RL` prefix.

    The negative half is the point: before the `^#{1,2}` widening this file produced no
    draft at all, so the assertion below is the one that fails on the unfixed regex.
    """
    doc_id = _load_by_path("_doc_id_under_test", DOC_ID_SCRIPT_PATH)

    # `_discover_multi_ruling_files` looks only under `docs/plans/`, and only at a
    # `YYYY-MM-DD-`-prefixed filename, so the fixture has to have both shapes for the
    # heading level to be the thing under test.
    plans_dir = tmp_path / "docs" / "plans"
    plans_dir.mkdir(parents=True)
    (plans_dir / "2026-09-04-a-single-hash-ruling.md").write_text(
        f"# {_R} {_FIXTURE_NUMBER} — A ruling written with a single-hash heading\n"
        "\n"
        "An H1 heading, not the H2 the discovery regex used to require.\n",
        encoding="utf-8",
    )

    discovered = doc_id._discover_multi_ruling_files(tmp_path)

    # `old_token`, not `title`: `title` is the heading text *after* the em-dash, so a
    # filter on the token appearing in `d.title` silently matches nothing and the test
    # passes vacuously on the unfixed regex too.
    matched = [d for d in discovered if d.old_token == f"{_R} {_FIXTURE_NUMBER}"]
    assert matched, "an H1 ruling heading should be discovered"
    assert [d for d in matched if d.prefix == "RL"], "an H1 ruling should be given RL"
    assert matched[0].title == "A ruling written with a single-hash heading"


def test_ruling_heading_re_matches_h1_and_h2() -> None:
    """Both heading levels match, and each yields its own ruling number."""
    doc_id = _load_by_path("_doc_id_under_test", DOC_ID_SCRIPT_PATH)

    h1 = doc_id._RULING_HEADING_RE.search(f"# {_R} {_H1_NUMBER} — A first-level heading")
    h2 = doc_id._RULING_HEADING_RE.search(f"## {_R} {_H2_NUMBER} — A second-level heading")

    assert h1 is not None, "an H1 ruling heading should match"
    assert h2 is not None, "an H2 ruling heading should still match"
    assert h1.group(1) == str(_H1_NUMBER)
    assert h2.group(1) == str(_H2_NUMBER)


def test_a_deeper_heading_is_not_a_ruling_heading() -> None:
    """`###` and deeper stay out: the widening is to `^#{1,2}`, not to any depth.

    Without this the regex could be loosened to `^#+` and every test above would still
    pass, so this is the case that pins the bound rather than the direction.
    """
    doc_id = _load_by_path("_doc_id_under_test", DOC_ID_SCRIPT_PATH)

    deeper = f"### {_R} {_DEEP_NUMBER} — A third-level heading"
    assert doc_id._RULING_HEADING_RE.search(deeper) is None
