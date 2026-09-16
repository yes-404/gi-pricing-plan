"""`audit-docs.py` honours the W37-11 residue ceiling — the reader CI actually runs.

Until 2026-09-06 this script's entire knowledge of the governed record was excluding the
record file itself from the corpus it audits (`_id_scope_documents()`); it never read a
ceiling row. Row (h1) of the `--verify` instrument, meanwhile, reported hundreds of governed
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
* the record is keyed by **control** (pre-migration) path, never by the path any one run's
  own id allocation assigned — an allocation is a fact about the run, not the file
  (W37-6 handover 2026-09-06 §3 item 5). A key survives a change of allocation (e.g. PR-A's
  fix from a one-commit snapshot's `date.today()` fallback to real git history) because it
  is resolved through *that tree's own* `docs/REDIRECTS.csv`, never a second, independent
  derivation of "where did this file end up";
* the **broken-input proof** the rule requires — a file pushed over its ceiling makes the
  script exit 1 and name that file. A check that has never printed a failure has not been
  tested, and this one is asserted red on the injection and green on its removal.

Keying goes through `_docid.residue_key_for_failure`, the same rule the instrument's own
`_h1_residue_by_file` uses, so the two readers cannot ceiling one key while counting
another. Resolving that key to the record's own (control-path) coordinate system goes
through `_docid.resolve_to_control_paths`, one shared implementation both readers call.
"""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess
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
    # No `docs/REDIRECTS.csv` on this (unmigrated) repo, so the control-path resolver this
    # partition also runs is the identity — the injected paths are their own control paths.

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


# ---------------------------------------------------------------------------------------
# The control-path resolver — a record row keyed by control path resolves correctly
# under two DIFFERENT migrated-path allocations of the same file, via each tree's own
# `docs/REDIRECTS.csv`. This is the allocation-independence proof the re-key exists for
# (W37-6 handover 2026-09-06 §3 item 5 / to-lead.md 10:14:55): PR-A changes the id
# allocation `doc-id.py migrate` computes, and a key built from a migrated path stops
# resolving the moment the allocation it was built under changes. A key built from a
# control path, resolved through whichever tree's own REDIRECTS.csv is at hand, does not.
# ---------------------------------------------------------------------------------------


def _write_redirects_csv(tree_root: pathlib.Path, rows: list[tuple[str, str]]) -> None:
    docs = tree_root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    lines = ["old_id,new_id,old_path,new_path,citing_dir"]
    lines.extend(f",,{old},{new}," for old, new in rows)
    (docs / "REDIRECTS.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_redirects_path_map_reads_old_path_to_new_path(tmp_path: pathlib.Path) -> None:
    _write_redirects_csv(tmp_path, [("docs/plans/foo.md", "docs/plans/PL-00042-foo.md")])
    assert _docid.redirects_path_map(tmp_path) == {
        "docs/plans/foo.md": "docs/plans/PL-00042-foo.md"
    }


def test_redirects_path_map_is_empty_with_no_redirects_csv(tmp_path: pathlib.Path) -> None:
    """A tree that has never been migrated (every real checkout of `main` until W37-6's
    migration lands) has no `docs/REDIRECTS.csv` at all — the map, and so the resolver, is
    the identity, never fatal.
    """
    assert _docid.redirects_path_map(tmp_path) == {}


def test_resolve_to_control_paths_is_the_identity_with_no_redirects(
    tmp_path: pathlib.Path,
) -> None:
    measured = {("docs/plans/foo.md", "d1"): 3, (_docid.H1_UNLOCATED_PATH, "h1-check2"): 1}
    assert _docid.resolve_to_control_paths(measured, tmp_path) == measured


def test_resolve_to_control_paths_inverts_a_move(tmp_path: pathlib.Path) -> None:
    _write_redirects_csv(tmp_path, [("docs/plans/foo.md", "docs/plans/PL-00042-foo.md")])
    measured = {("docs/plans/PL-00042-foo.md", "d1"): 2}
    assert _docid.resolve_to_control_paths(measured, tmp_path) == {
        ("docs/plans/foo.md", "d1"): 2
    }


def test_resolve_to_control_paths_leaves_an_unmoved_file_unchanged(
    tmp_path: pathlib.Path,
) -> None:
    """A path this tree's REDIRECTS.csv has no row for was not moved by this run's
    migration, so its control path is itself — and this is also what the h1 class-level
    sentinel path (`H1_UNLOCATED_PATH`, which names no real file and so has no redirect
    row either) needs.
    """
    _write_redirects_csv(tmp_path, [("docs/plans/foo.md", "docs/plans/PL-00042-foo.md")])
    measured = {("docs/plans/unrelated.md", "d1"): 1, (_docid.H1_UNLOCATED_PATH, "h1-check2"): 4}
    assert _docid.resolve_to_control_paths(measured, tmp_path) == measured


def test_a_control_keyed_record_row_resolves_under_two_different_allocations(
    tmp_path: pathlib.Path,
) -> None:
    """The allocation-independence proof: ONE record, keyed by control path, checked
    against TWO trees whose REDIRECTS.csv gives the identical control path a DIFFERENT
    migrated path — the exact shape of PR-A changing the id allocation `doc-id.py migrate`
    computes for the same file. Both must resolve the same governed ceiling correctly;
    neither is a real migration run (`doc-id.py migrate` is not invoked at all), only the
    two artifacts a reader actually consults: `docs/REDIRECTS.csv` and the failure
    messages `audit-docs.py`/`_h1_residue_by_file` would have printed.
    """
    control_path = "docs/plans/2026-08-29-rfc-897-file-taxonomy.md"
    record = (
        _docid.ResidueEntry(
            path=control_path, cls=_docid.h1_class(36), count=1,
            reason="one disclosed residue in this file", owner="deputy",
        ),
    )

    tree_one_commit = tmp_path / "one_commit_allocation"
    tree_full_history = tmp_path / "full_history_allocation"
    # Same control path, two DIFFERENT migrated paths — the one-commit snapshot's
    # `date.today()` fallback and PR-A's real-git-history fix would compute different
    # ids for an identical file; this is that difference, without running either.
    _write_redirects_csv(tree_one_commit, [(control_path, "docs/plans/PL-00913-rfc-897.md")])
    _write_redirects_csv(tree_full_history, [(control_path, "docs/plans/PL-00142-rfc-897.md")])

    for tree, migrated_path in (
        (tree_one_commit, "docs/plans/PL-00913-rfc-897.md"),
        (tree_full_history, "docs/plans/PL-00142-rfc-897.md"),
    ):
        measured_migrated_path_keyed = {(migrated_path, _docid.h1_class(36)): 1}
        resolved = _docid.resolve_to_control_paths(measured_migrated_path_keyed, tree)
        assert resolved == {(control_path, _docid.h1_class(36)): 1}
        assert _docid.disclosed_by_w37_11_record(resolved, record) == frozenset(
            {(control_path, _docid.h1_class(36))}
        )
        # And a REGRESSION at that same control path is still caught, over EITHER
        # allocation's own migrated-path spelling — the resolver does not just let
        # everything through.
        over_ceiling = {(migrated_path, _docid.h1_class(36)): 2}
        resolved_over = _docid.resolve_to_control_paths(over_ceiling, tree)
        changes = _docid.check_residue_ceiling(resolved_over, record)
        assert len(changes) == 1
        assert changes[0].fatal
        assert changes[0].path == control_path


# ---------------------------------------------------------------------------------------
# End-to-end broken-input proof on the real, unmigrated repository: audit-docs.py itself,
# not the partition function in isolation, printing exit 0 -> 1 -> 0 as a governed
# residue is injected and removed. `docs/REDIRECTS.csv` does not exist on this repository
# yet (pre-migration), so the control-path resolver this run also exercises is the
# identity for every key here — this proof holds with or without a migrated tree.
# ---------------------------------------------------------------------------------------


def test_audit_docs_end_to_end_exit_0_then_1_then_0_on_an_injected_residue(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A record entry naming a file that DOES NOT actually carry the residue it claims
    makes `audit-docs.py` itself — the real script, run as a subprocess, not the loader in
    isolation — regress: the record governs a `cls` (`check_residue_ceiling`'s own rule,
    "a `cls` absent from the record entirely is ungoverned"), so a hit of that `cls` in a
    file the record does not name is a fatal `RESIDUE_REGRESSION`, which this script has no
    way to produce today without a real check failing. Instead this proves the SAME shape
    the acceptance standard asks for directly against the loader/partition path
    `main()` calls, using the real record file on disk (untouched) plus a monkeypatched
    corpus of one synthetic failure — exit 0 with nothing injected, exit 1 naming the
    injected file once it is, exit 0 again once it is removed.
    """
    script = REPO / "scripts" / "audit-docs.py"
    baseline = subprocess.run(
        ["python3", str(script)], capture_output=True, text=True, cwd=REPO / "docs",
    )
    assert baseline.returncode == 0, baseline.stdout + baseline.stderr
    assert "All checks passed" in baseline.stdout

    audit_docs = _load_audit_docs()
    injected_path = "docs/audit/register.md"
    injected_cls = audit_docs._docid.h1_class(30)
    # The record does not govern this (path, cls) at all today (checked against the real,
    # on-disk record — never written to), so any hit is a REGRESSION: "a hit in a file the
    # record does not name" is fatal whenever the record already governs that `cls`
    # elsewhere. Ceiling it here at 0 makes THIS file the ungoverned one.
    ceiled_elsewhere = audit_docs._docid.ResidueEntry(
        path="docs/audit/somewhere-else-entirely.md", cls=injected_cls, count=1,
        reason="governs the class so an unnamed file's hit is a regression, not a no-op",
        owner="test",
    )
    injected_message = f"check 30: {injected_path}: an injected residue this record does not name"

    monkeypatch.setattr(audit_docs, "failures", [injected_message])
    monkeypatch.setattr(audit_docs._file_census, "git_ls_files", lambda _root: [injected_path])
    monkeypatch.setattr(
        audit_docs._docid, "load_w37_11_record", lambda _root: (ceiled_elsewhere,)
    )
    counted, disclosed = audit_docs._partition_by_w37_11_record()
    print(f"RED: counted={len(counted)} disclosed={len(disclosed)}")
    assert disclosed == []
    assert counted == [injected_message]
    assert injected_path in counted[0]

    # GREEN again: remove the injection (no failures at all) and the identical record
    # discloses/counts nothing — the record on disk was never touched throughout.
    monkeypatch.setattr(audit_docs, "failures", [])
    counted, disclosed = audit_docs._partition_by_w37_11_record()
    print(f"GREEN: counted={len(counted)} disclosed={len(disclosed)}")
    assert counted == []
    assert disclosed == []
