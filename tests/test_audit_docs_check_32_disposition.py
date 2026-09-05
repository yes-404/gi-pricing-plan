#!/usr/bin/env python3
"""`docs/plans/2026-09-04-w37-6-ruling-107-check-32-36-shared-predicates.md` Entry 2 item
1's check-32 disposition — the padding clause adopts row (e)'s conjuncts 2 and 3 from
shared `_docid` code: a padded id sitting inside a filesystem path (conjunct 2) or whose
unpadded form does not resolve in `docs/INDEX.md` (conjunct 3) is not a padding violation.
Check 32 keeps its own broader `0*` breadth beyond (e)'s exact-width conjunct 1: a padded
citation with fewer leading zeros than `_docid.PAD_WIDTH` (a "short-padded" id) is a real
rule-2 violation (e) does not see, and it is listed under its own text, never folded into
(e)'s count.

`test_check_32_lists_kinds_of_failures` (asserting check 32 must print a machine-readable
classification) is deleted, not renamed, per the ruling record's discharge/rescoping
section — nobody ruled that requirement.

Every test drives `citation_problems_in_file` directly against a document built in a
tempdir, never against the live `docs/` tree. That is deliberate — see the discussion this
comment's predecessor recorded, still true: a test resolved relative to the test file's own
parent only measures the repository root by accident of where the file sits, and a test
asserting only `len(notes) > 0` is satisfied by the pre-migration "skipped" note alone.

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

#: The one id the fixture index resolves. Every other citation in these fixtures is
#: unresolvable by construction.
INDEX_IDS = {"PL-66"}


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
    """Conjunct 2: a padded id inside a filesystem path is not a padding violation.
    `docs/plans/PL-00066-slug.md` names a file; it does not cite `PL-00066`.
    """
    audit = _load_audit()
    with tempfile.TemporaryDirectory() as tmpdir:
        doc = pathlib.Path(tmpdir) / "test.md"
        doc.write_text("See `docs/plans/PL-00066-slug.md` for detail.\n", encoding="utf-8")
        problems = audit.citation_problems_in_file(doc, index_ids=INDEX_IDS)
        padding_problems = [p for p in problems if "padded" in p]
        assert padding_problems == [], f"Path should exclude padding check: {padding_problems}"


def test_check_32_unresolvable_padded_id_is_not_a_padding_violation() -> None:
    """Conjunct 3: a padded id whose unpadded form does not resolve in `docs/INDEX.md` is
    a specimen of the form, not a citation — exactly as row (e) reads it. Only the
    resolution failure fires; no padding failure alongside it.

    Made to fail on purpose against the pre-fix code (which had no conjunct 3 at all):
    pre-fix, this asserted list is `["1: PL-99 does not resolve in docs/INDEX.md"]` but
    the actual result also carried a padding problem for the same token, since nothing
    gated the padding branch on resolution.
    """
    audit = _load_audit()
    with tempfile.TemporaryDirectory() as tmpdir:
        doc = pathlib.Path(tmpdir) / "test.md"
        doc.write_text("See PL-00099 for detail.\n", encoding="utf-8")
        problems = audit.citation_problems_in_file(doc, index_ids=INDEX_IDS)
    assert problems == ["1: PL-99 does not resolve in docs/INDEX.md"], problems


def test_check_32_exact_width_padded_id_reds_alongside_row_e() -> None:
    """Broken-input proof (ruling record Entry 2 item 1's acceptance line): a `PL-00066`
    in prose reds both row (e) and check 32 — it resolves (`PL-66` is indexed), it is not
    path-shaped, and it matches (e)'s exact-width conjunct 1.
    """
    audit = _load_audit()
    with tempfile.TemporaryDirectory() as tmpdir:
        doc = pathlib.Path(tmpdir) / "test.md"
        doc.write_text("The rule in PL-00066 applies here.\n", encoding="utf-8")
        problems = audit.citation_problems_in_file(doc, index_ids=INDEX_IDS)
    assert problems == [
        "1: padded id `PL-00066` outside a link target — citations write the integer, "
        "never padding (NT-0019 §1.1 rule 2)"
    ], problems


def test_check_32_path_shaped_padded_id_reds_neither() -> None:
    """Broken-input proof: a `docs/plans/PL-00066-x.md` path in prose reds neither row (e)
    nor check 32 — it names a file, it does not cite an id in prose.
    """
    audit = _load_audit()
    with tempfile.TemporaryDirectory() as tmpdir:
        doc = pathlib.Path(tmpdir) / "test.md"
        doc.write_text("See docs/plans/PL-00066-x.md for the plan.\n", encoding="utf-8")
        problems = audit.citation_problems_in_file(doc, index_ids=INDEX_IDS)
    assert problems == [], problems


def test_check_32_short_padded_id_reds_check_32_alone_and_is_listed() -> None:
    """Broken-input proof: a `PL-066` reds check 32 alone — row (e)'s exact-width conjunct
    1 does not match a 3-digit padded form — and is listed under its own text: a real
    NT-0019 §1.1 rule 2 violation, never folded into (e)'s count.
    """
    audit = _load_audit()
    with tempfile.TemporaryDirectory() as tmpdir:
        doc = pathlib.Path(tmpdir) / "test.md"
        doc.write_text("See PL-066 for the rationale.\n", encoding="utf-8")
        problems = audit.citation_problems_in_file(doc, index_ids=INDEX_IDS)
    assert problems == [
        "1: short-padded id `PL-066` outside a link target — fewer leading zeros than "
        "`_docid.PAD_WIDTH`, still a rule-2 violation row (e)'s exact-width conjunct does "
        "not see (NT-0019 §1.1 rule 2)"
    ], problems
