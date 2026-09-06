"""`audit-docs.py` honours the W37-11 residue ceiling — the reader CI actually runs.

Until 2026-09-06 this script's entire knowledge of the governed record was excluding the
record file itself from the corpus it audits (`_id_scope_documents()`); it never read a
ceiling row. Row (h1) of the `--verify` instrument, meanwhile, reported 806 governed
failures that `audit-docs.py` "cannot itself resolve". The consequence was structural
rather than incidental: the `docs` gate was red on every migrated tree — including `main`
once the migration merged — for the whole of W37-11's duration, and no amount of correct
disclosure elsewhere could turn it green.

What is pinned here:

* a `(path, cls)` at or under its recorded ceiling is **disclosed** — printed by name under
  a named header, and not counted into the tally that decides the exit code;
* a `(path, cls)` **over** its ceiling fails as it did before, and in full: the ceiling
  exists to make the moment it stops being honoured loud, so disclosing the first `limit`
  of `limit + 1` hits would be exactly backwards;
* a file the record does not name for that class fails as it did before;
* the **broken-input proof** the rule requires — a file pushed over its ceiling makes the
  script exit 1 and name that file. A check that has never printed a failure has not been
  tested, and this one is asserted red on the injection and green on its removal.

Keying goes through `_docid.residue_key_for_failure`, the same rule the instrument's own
`_h1_residue_by_file` uses, so the two readers cannot ceiling one key while counting
another.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import types
from typing import Final

import pytest

REPO: Final = pathlib.Path(__file__).resolve().parents[1]
AUDIT_DOCS_PATH: Final = REPO / "scripts" / "audit-docs.py"

if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

def _load_by_path(name: str, path: pathlib.Path) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_audit_docs() -> types.ModuleType:
    return _load_by_path("_audit_docs_ceiling_under_test", AUDIT_DOCS_PATH)


# Loaded by path rather than `import _docid`: `scripts/` is not a package on mypy's own
# path, so a plain import is an unresolvable stub for it even though it resolves at run
# time through the `sys.path` insertion above.
_docid: types.ModuleType = _load_by_path("_docid_for_ceiling_test", REPO / "scripts" / "_docid.py")


@pytest.fixture(scope="module")
def audit_docs() -> types.ModuleType:
    return _load_audit_docs()


ENTRY: Final = _docid.ResidueEntry(
    path="docs/audit/register.md",
    cls=_docid.h1_class(30),
    count=2,
    reason="a disclosed residue, for this test only",
    owner="deputy",
)


def test_a_key_at_its_ceiling_is_disclosed() -> None:
    measured = {(ENTRY.path, ENTRY.cls): 2}
    assert _docid.disclosed_by_w37_11_record(measured, [ENTRY]) == frozenset(
        {(ENTRY.path, ENTRY.cls)}
    )


def test_a_key_under_its_ceiling_is_disclosed() -> None:
    measured = {(ENTRY.path, ENTRY.cls): 1}
    assert _docid.disclosed_by_w37_11_record(measured, [ENTRY]) == frozenset(
        {(ENTRY.path, ENTRY.cls)}
    )


def test_a_key_over_its_ceiling_is_not_disclosed_at_all() -> None:
    """Not "disclosed down to the ceiling" — not disclosed at all.

    Partial disclosure would report a ceiling still being honoured at the exact moment it
    stopped being, which is the one moment the record exists to make loud.
    """
    measured = {(ENTRY.path, ENTRY.cls): 3}
    assert _docid.disclosed_by_w37_11_record(measured, [ENTRY]) == frozenset()


def test_a_file_the_record_does_not_name_is_not_disclosed() -> None:
    measured = {("docs/audit/somewhere-else.md", ENTRY.cls): 1}
    assert _docid.disclosed_by_w37_11_record(measured, [ENTRY]) == frozenset()


def test_an_empty_record_discloses_nothing() -> None:
    """A row cannot close by DISCLOSE on an empty record — the vacuous-truth guard."""
    assert _docid.disclosed_by_w37_11_record({(ENTRY.path, ENTRY.cls): 1}, []) == frozenset()


def test_both_readers_key_a_failure_message_identically() -> None:
    """One keying rule, or the record ceilings one key while the gate counts another."""
    msg = "check 30: docs/audit/register.md: owner: names no role file"
    known = frozenset({"docs/audit/register.md"})
    assert _docid.residue_key_for_failure(msg, known) == (
        "docs/audit/register.md", _docid.h1_class(30)
    )
    # Resolution, not shape: a token that looks like a path but names no file in the
    # corpus falls to the class-level sentinel rather than inventing a per-file ceiling.
    assert _docid.residue_key_for_failure(msg, frozenset()) == (
        _docid.H1_UNLOCATED_PATH, _docid.h1_class(30)
    )
    # No check number at all — nothing to key on, and the caller must count it.
    assert _docid.residue_key_for_failure("something with no prefix", known) is None


def test_the_partition_discloses_at_the_ceiling_and_fails_over_it(
    audit_docs: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The broken-input proof, at the partition that decides the exit code.

    Red on the injection, green on its removal, in one test so the two readings cannot
    drift apart: the same two failure messages are disclosed under a ceiling of 2 and
    counted — every one of them, and by name — under a ceiling of 1.
    """
    messages = [
        "check 30: docs/audit/register.md: owner: names no role file",
        "check 30: docs/audit/register.md: a second failure in the same file",
    ]
    monkeypatch.setattr(audit_docs, "failures", list(messages))
    monkeypatch.setattr(
        audit_docs._file_census, "git_ls_files", lambda _root: ["docs/audit/register.md"]
    )

    # `audit-docs.py` loads `_docid` by path (a hyphenated filename is not an `import`
    # target), so its `_docid` is a *different module object* from this test's import of
    # the same file. The patch has to land on the one the script actually reads, or the
    # real record is loaded and the test measures nothing it set up.
    # GREEN: the record names this file at a ceiling of 2, and 2 were measured.
    monkeypatch.setattr(audit_docs._docid, "load_w37_11_record", lambda _root: (ENTRY,))
    counted, disclosed = audit_docs._partition_by_w37_11_record()
    assert counted == []
    assert disclosed == messages

    # RED: the identical measurement against a ceiling of 1 is over it, so every one of
    # the two is counted and the file is named in what the script would print.
    over = _docid.ResidueEntry(
        path=ENTRY.path, cls=ENTRY.cls, count=1, reason=ENTRY.reason, owner=ENTRY.owner
    )
    monkeypatch.setattr(audit_docs, "failures", list(messages))
    monkeypatch.setattr(audit_docs._docid, "load_w37_11_record", lambda _root: (over,))
    counted, disclosed = audit_docs._partition_by_w37_11_record()
    assert disclosed == []
    assert counted == messages
    assert all("docs/audit/register.md" in msg for msg in counted)


def test_a_record_naming_an_unproducible_class_fails_loudly(
    audit_docs: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An unloadable governance table must not silently become an empty one.

    An empty record counts everything, which reads as an ordinary regression; the real
    fault — a row keyed on a label no extractor emits, governing nothing forever — would
    never be named. So the loader raises, and the exception is left to propagate out of the
    partition for `main` to report under its own heading and exit 1 on.

    Deliberately not swallowed into a `fail()` message: every `fail()` in this script must
    open with its own `check N: ` prefix so row (h1) can key it
    (`tests/test_audit_docs_check_prefixes.py`, which caught this the first time round).
    This fault belongs to no check and names no document.
    """
    monkeypatch.setattr(audit_docs, "failures", [])

    def _raise(_root: pathlib.Path) -> tuple[object, ...]:
        # The script's own module object, so the `except` clause in the partition matches.
        raise audit_docs._docid.InvalidResidueClassError("'not-a-real-class' is not a class")

    monkeypatch.setattr(audit_docs._docid, "load_w37_11_record", _raise)
    with pytest.raises(audit_docs._docid.InvalidResidueClassError, match="not-a-real-class"):
        audit_docs._partition_by_w37_11_record()


def test_an_unknown_class_is_rejected_by_the_shared_registry() -> None:
    """The registry is derived from each extractor's own constructor, so a produced class
    is accepted and a hand-typed description of a cause is not.
    """
    assert _docid.known_w37_11_class(_docid.h1_class(36))
    assert _docid.known_w37_11_class(_docid.d_row_class(1))
    assert _docid.known_w37_11_class(_docid.g2_class(_docid.CAUSE_6_PYCACHE))
    assert not _docid.known_w37_11_class("comma-continuation-left-whole")
    assert not _docid.known_w37_11_class(_docid.g2_class("a-cause-nothing-returns"))
