#!/usr/bin/env python3
"""Ruling 107's check-32 disposition — the path exclusion, and the kinds of failure
check 32 reports.

Ruling 107 item 1.1 adopts conjunct 2 of `(e)` from `_docverify.py`: a padded id sitting
inside a filesystem path is not a citation violation, because it is naming a file rather
than citing an id in prose. Item 2 requires check 32's failures to be distinguishable by
kind — resolution, padding, and link text/target mismatch.

Both tests drive `citation_problems_in_file` directly against a document built in a
tempdir, never against the live `docs/` tree. That is deliberate. The predecessor of the
second test called `check_citations()` over the real tree, resolved relative to the test
file's own parent — which was the repository root only by accident of where the file then
sat, so moving the file would have silently changed what it measured. It also asserted
only `len(notes) > 0`, which the pre-migration "no docs/INDEX.md yet, skipped" note
satisfies on its own: deleting the whole body of check 32 left it green.

This file lives under `tests/` rather than at the repository root because
`pyproject.toml`'s `testpaths` does not list the root, so a root-level test file is never
collected — the fifth occurrence of the defect the comment above that list records four
of.
"""

import importlib.util
import pathlib
import sys
import tempfile
import types

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "audit-docs.py"

#: The one id the fixture index resolves. Everything else in the fixture document is
#: unresolvable by construction, which is what makes the resolution kind fire.
INDEX_IDS = {"PL-66"}

#: A document carrying exactly one failure of each kind, plus one deliberate non-failure.
#: Line 4 is the discriminator: before Ruling 107's path exclusion it was reported as a
#: padding violation, and it is the reason `len(problems)` is asserted rather than only
#: the three kinds being present.
BROKEN_DOC = (
    "See PL-77 for the rationale.\n"  # 1 — resolution: PL-77 is not in the index
    "The rule in PL-00066 applies here.\n"  # 2 — padding: resolves, but written padded
    "[PL-66](docs/plans/PL-77-other.md)\n"  # 3 — mismatch: text and target differ
    "See docs/plans/PL-00066-slug.md for the plan.\n"  # 4 — NOT a failure: a path
)

EXPECTED_RESOLUTION = "1: PL-77 does not resolve in docs/INDEX.md"
EXPECTED_PADDING = (
    "2: padded id `PL-00066` outside a link target — citations write the integer, "
    "never padding (NT-0019 §1.1 rule 2)"
)


def _load_audit() -> types.ModuleType:
    """Load `audit-docs.py` by path — a hyphenated `scripts/` module cannot be `import`ed
    by name. A per-file loader rather than a shared conftest helper, matching
    `tests/test_audit_docs_ids.py`, which carries its own.
    """
    spec = importlib.util.spec_from_file_location("_audit_docs_check_32", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_check_32_path_excluded_from_padding_check() -> None:
    """Ruling 107 item 1.1: a padded id inside a filesystem path is not a padding
    violation. `docs/plans/PL-00066-slug.md` names a file; it does not cite `PL-00066`.
    """
    audit = _load_audit()
    with tempfile.TemporaryDirectory() as tmpdir:
        doc = pathlib.Path(tmpdir) / "test.md"
        doc.write_text("See `docs/plans/PL-00066-slug.md` for detail.\n", encoding="utf-8")
        problems = audit.citation_problems_in_file(doc, index_ids=INDEX_IDS)
        padding_problems = [p for p in problems if "padded" in p]
        assert padding_problems == [], f"Path should exclude padding check: {padding_problems}"


def test_check_32_lists_kinds_of_failures() -> None:
    """Ruling 107 item 2: check 32's failures are distinguishable by kind — resolution,
    padding, and link text/target mismatch — and each names the line it is on.

    Asserted against a deliberately broken document rather than the live tree, and on the
    problems' actual text rather than their count. The fourth line is a padded id in a
    path: it must contribute nothing, which is why the total is pinned at three.
    """
    audit = _load_audit()
    with tempfile.TemporaryDirectory() as tmpdir:
        doc = pathlib.Path(tmpdir) / "broken.md"
        doc.write_text(BROKEN_DOC, encoding="utf-8")
        problems = audit.citation_problems_in_file(doc, index_ids=INDEX_IDS)

    resolution = [p for p in problems if "does not resolve in docs/INDEX.md" in p]
    padding = [p for p in problems if "padded id" in p]
    mismatch = [p for p in problems if "cites" in p and "names" in p]

    assert resolution == [EXPECTED_RESOLUTION], problems
    assert padding == [EXPECTED_PADDING], problems
    assert len(mismatch) == 1, problems
    assert mismatch[0].startswith("3: link text 'PL-66' cites PL-66 but its target "), problems
    assert "names PL-77" in mismatch[0], problems

    # The three kinds are the whole of it: line 4's padded id in a path is excluded, so a
    # regression that reinstated it would show up here as a fourth problem.
    assert len(problems) == 3, problems
