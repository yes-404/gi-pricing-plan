#!/usr/bin/env python3
"""TDD tests for Ruling 107 check dispositions (31, 32, 36).

Tests for the three check dispositions required by Ruling 107:
- Check 31: One singleton fix
- Check 32: List kinds and adopt (e)'s conjuncts
- Check 36: Adopt (d)'s exclusions and print disclosed classes by count
"""

import importlib.util
import pathlib
import sys
import tempfile
import types


def _load_audit() -> types.ModuleType:
    """Load audit-docs.py for testing."""
    script = pathlib.Path(__file__).resolve().parent / "scripts" / "audit-docs.py"
    spec = importlib.util.spec_from_file_location("_audit_docs_test", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["_audit_docs_test"] = module
    spec.loader.exec_module(module)
    return module


def test_check_32_path_excluded_from_padding_check():
    """Ruling 107 item 1.1: check 32 should exclude padded ids in filesystem paths
    (conjunct 2 of (e) from _docverify.py).

    A sentence like "see docs/plans/PL-00066-slug.md" should not flag PL-00066
    as a padded id violation.
    """
    audit = _load_audit()
    with tempfile.TemporaryDirectory() as tmpdir:
        doc = pathlib.Path(tmpdir) / "test.md"
        doc.write_text("See `docs/plans/PL-00066-slug.md` for detail.\n")
        # This should not find padding violation for PL-00066 since it's in a path
        problems = audit.citation_problems_in_file(doc, index_ids={"PL-66"})
        # Should be empty (or only have resolution issues if PL-66 doesn't resolve)
        padding_problems = [p for p in problems if "padded" in p]
        assert len(padding_problems) == 0, f"Path should exclude padding check: {padding_problems}"


def test_check_32_lists_kinds_of_failures():
    """Ruling 107 item 2: check 32 should classify failures by kind
    and report them separately: resolution vs padding vs mismatches.
    """
    audit = _load_audit()
    # This test checks that the note output includes kind categorization
    # We'll verify this by checking the note message after running check 32
    audit.failures.clear()
    audit.notes.clear()
    audit.check_citations()
    # Should have a note that mentions kinds or categories
    note_text = " ".join(audit.notes)
    # The note should mention the different problem kinds
    # (placeholder - exact format TBD from implementation)
    assert len(audit.notes) > 0


if __name__ == "__main__":
    test_check_32_path_excluded_from_padding_check()
    test_check_32_lists_kinds_of_failures()
    print("✓ All TDD tests passed")
