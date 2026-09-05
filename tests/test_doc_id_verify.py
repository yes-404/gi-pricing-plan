"""Tests for `scripts/doc-id.py migrate --verify` — Ruling 102 §1's instrument.

**The broken-input proofs `CLAUDE.md` §13 requires.** *"A check that has never printed a
failure has not been tested."* Every row's predicate below is exercised **red-then-green**:
a clean synthetic corpus makes the row pass, one deliberate mutation makes it fail, and the
test asserts the transition rather than either state alone. A row whose predicate could not
be made to fail on demand would be a row this suite could not certify.

Three of the proofs are named by the record rather than invented here:

* **(g)** — Ruling 102 §2 row 1: *"`NFR-RATE-13/14` is the broken-input proof"*. The exact
  mangling it names, `NFR-RATE-13/14` → `NFR-775/14`, is the input.
* **(d)'s `was:` exclusion** — Ruling 102 §5: the exemption keys on the parsed field, never
  a substring. The proof is a corpus where a substring test and a field test give different
  answers, and the field test is asserted.
* **the empty-population rule** — `docs/notes/0007-context-bound-measures-cap-not-discipline.md`:
  a green over a zero denominator is a fail. The proof is an empty corpus that must **not**
  come back green.

No `@pytest.mark.req` marker, for the reason `tests/test_doc_id_migrate.py`'s module
docstring gives: this is correctness of a tool, not evidence for a numbered platform
requirement.
"""

from __future__ import annotations

import importlib.util
import os
import pathlib
import re
import subprocess
import sys
from typing import Any, Final

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOC_ID_SCRIPT_PATH = ROOT / "scripts" / "doc-id.py"

if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))


def _load_by_path(name: str, path: pathlib.Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def dv() -> Any:
    """`scripts/_docverify.py`, loaded by path like every other script under test here.

    Typed `Any` rather than `ModuleType` so the row dataclasses it hands back
    (`Snapshot`, `Row`) keep their attributes under `mypy --strict`; a `ModuleType`
    annotation makes every `snap.migrated` an attribute error.
    """
    return _load_by_path("_docverify_under_test", ROOT / "scripts" / "_docverify.py")


@pytest.fixture(scope="module")
def doc_id_cli() -> Any:
    return _load_by_path("_doc_id_verify_under_test", DOC_ID_SCRIPT_PATH)


# ---------------------------------------------------------------------------------------
# A tiny two-tree snapshot, so a row's predicate can be exercised without a 60-second
# migration. The trees are real git repositories because that is what the rows read.
# ---------------------------------------------------------------------------------------


def _mkrepo(root: pathlib.Path, files: dict[str, str]) -> pathlib.Path:
    root.mkdir(parents=True, exist_ok=True)
    for rel, text in files.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "init", "-q", "-b", "snapshot"], check=True)
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(
        ["git", "-C", str(root), "-c", "user.email=t@t", "-c", "user.name=t",
         "commit", "-q", "-m", "snapshot"],
        check=True,
    )
    return root


def _snapshot(
    dv: Any,
    tmp_path: pathlib.Path,
    migrated: dict[str, str],
    control: dict[str, str],
) -> Any:
    workdir = tmp_path / "wd"
    workdir.mkdir(parents=True)
    (workdir / dv.SENTINEL_NAME).write_text("{}\n", encoding="utf-8")
    return dv.Snapshot(
        workdir=workdir,
        ref="test",
        ref_sha="0" * 40,
        migrated=_mkrepo(workdir / dv.MIGRATED_DIR, migrated),
        control=_mkrepo(workdir / dv.CONTROL_DIR, control),
        baseline=None,
        baseline_ref=None,
    )


def _d_rows(dv: Any, snap: Any) -> dict[str, Any]:
    """(d)'s thirteen rows, keyed `d1`..`d13`."""
    return {
        row.key: row
        for row in dv.rows_d(dv.load_corpus(snap.migrated), dv.load_corpus(snap.control))
    }


# =========================================================================================
# The refusal: "a disposable snapshot, never a real checkout" (Ruling 102 §1)
# =========================================================================================


def test_verify_refuses_this_very_checkout(dv: Any) -> None:
    """The exact mistake the clause exists to prevent: `--verify` at the repository root.

    Broken input is the real repository, and the assertion is that the instrument *will
    not run* — a convention would merely have documented that it should not.
    """
    with pytest.raises(dv.WorkingCheckoutRefusedError):
        dv.assert_workdir_disposable(ROOT)


def test_verify_refuses_a_new_path_inside_a_checkout(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """A path that does not exist *yet* but would be created inside a work tree.

    The refusal must not be satisfiable by choosing a name nothing occupies: `migrate()`
    would still write ~1400 files into someone's checkout.
    """
    with pytest.raises(dv.WorkingCheckoutRefusedError):
        dv.assert_workdir_disposable(ROOT / "does-not-exist-yet" / "deeper")


def test_verify_refuses_a_non_empty_directory(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    occupied = tmp_path / "occupied"
    occupied.mkdir()
    (occupied / "someones-file.txt").write_text("x", encoding="utf-8")
    with pytest.raises(dv.WorkingCheckoutRefusedError):
        dv.assert_workdir_disposable(occupied)


def test_verify_refuses_a_file(dv: Any, tmp_path: pathlib.Path) -> None:
    target = tmp_path / "a-file"
    target.write_text("x", encoding="utf-8")
    with pytest.raises(dv.WorkingCheckoutRefusedError):
        dv.assert_workdir_disposable(target)


def test_verify_accepts_an_empty_directory_outside_a_checkout(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """The green half of the refusal proof: the guard is not simply always-refusing."""
    empty = tmp_path / "empty"
    empty.mkdir()
    dv.assert_workdir_disposable(empty)  # must not raise


def test_migrate_is_refused_a_tree_with_real_history(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """The second guard: a tree with more than one commit was not built by this run."""
    repo = _mkrepo(tmp_path / "wd" / "migrated", {"a.md": "one\n"})
    (repo.parent / dv.SENTINEL_NAME).write_text("{}\n", encoding="utf-8")
    dv.assert_tree_is_snapshot(repo)  # green: one commit, sentinel present, no remotes
    (repo / "b.md").write_text("two\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t",
         "commit", "-q", "-m", "second"],
        check=True,
    )
    with pytest.raises(dv.WorkingCheckoutRefusedError):
        dv.assert_tree_is_snapshot(repo)


def test_migrate_is_refused_a_tree_without_the_sentinel(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    repo = _mkrepo(tmp_path / "wd" / "migrated", {"a.md": "one\n"})
    with pytest.raises(dv.WorkingCheckoutRefusedError):
        dv.assert_tree_is_snapshot(repo)


def test_cli_refusal_exits_2_not_1(doc_id_cli: Any) -> None:
    """"I would not run" and "I ran and it is red" must not share an exit code.

    A CI step that cannot tell them apart reports a misconfiguration as a corpus defect.
    """
    assert doc_id_cli.main(["migrate", "--verify", str(ROOT)]) == 2


# =========================================================================================
# W37-6: `tracked_files`/`load_corpus` exclude a declared lockfile, a
# `tests/fixtures/docs-ids/`/`tests/fixtures/docs-migration/` path, and a
# `__pycache__`/`.pyc` artifact — the same `_docid.sweep_exclusion_reason` predicate
# `doc-id.py`'s `_iter_tree_files` reads (Ruling 67 §2's "one shared constant"), so every
# row built on `load_corpus` — not only (d) — never counts one of these three classes as
# residue.
# =========================================================================================


def test_tracked_files_excludes_a_declared_lockfile(dv: Any, tmp_path: pathlib.Path) -> None:
    repo = _mkrepo(tmp_path / "repo", {
        "docs/a.md": "a clean line\n",
        "uv.lock": "a coincidental NT-0001-shaped hash\n",
    })
    files = dv.tracked_files(repo)
    assert "docs/a.md" in files
    assert "uv.lock" not in files


def test_tracked_files_excludes_the_fixture_corpus_roots(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    repo = _mkrepo(tmp_path / "repo", {
        "docs/a.md": "a clean line\n",
        "tests/fixtures/docs-ids/sample.md": "NT-0001, deliberately legacy\n",
        "tests/fixtures/docs-migration/docs/notes/x.md": "NT-0002, deliberately legacy\n",
    })
    files = dv.tracked_files(repo)
    assert "docs/a.md" in files
    assert "tests/fixtures/docs-ids/sample.md" not in files
    assert "tests/fixtures/docs-migration/docs/notes/x.md" not in files


def test_tracked_files_excludes_pycache_and_pyc(dv: Any, tmp_path: pathlib.Path) -> None:
    repo = _mkrepo(tmp_path / "repo", {
        "docs/a.md": "a clean line\n",
        "scripts/__pycache__/foo.cpython-312.pyc": "binary stand-in\n",
    })
    files = dv.tracked_files(repo)
    assert "docs/a.md" in files
    assert not any("__pycache__" in rel for rel in files)


def test_load_corpus_never_scans_an_excluded_files_content(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """The exclusion holds at the corpus a row actually reads, not only at the file
    listing — a lockfile carrying a legacy-id-shaped string must contribute neither a line
    nor a file to `Corpus.scan`.
    """
    repo = _mkrepo(tmp_path / "repo", {
        "docs/a.md": "a clean line with no legacy citation\n",
        "uv.lock": "a coincidental NT-0001 inside generated data\n",
    })
    corpus = dv.load_corpus(repo)
    assert "uv.lock" not in corpus.files
    n_lines, n_files = corpus.scan(re.compile(r"\bNT-0001\b"))
    assert (n_lines, n_files) == (0, 0)


def test_run_script_disables_bytecode_caching_in_the_subprocess(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """`_run_script` launches `python <snapshot>/scripts/<script>` as a subprocess, whose
    own imports (`doc-index.py` loading `_docid.py`, `doc-id.py`, …) would otherwise cache
    `.pyc` files into the snapshot's `scripts/__pycache__/` — a second, independent writer
    of the same exhaust `doc-id.py`'s in-process `_load_module` fix stops. Proven by
    asking the subprocess itself what it saw in its own environment, not by mocking
    `subprocess.run`.
    """
    repo = _mkrepo(tmp_path / "repo", {"docs/a.md": "x\n"})
    probe = repo / "scripts" / "probe.py"
    probe.parent.mkdir(parents=True, exist_ok=True)
    probe.write_text(
        "import os\nprint(os.environ.get('PYTHONDONTWRITEBYTECODE', ''))\n",
        encoding="utf-8",
    )
    result = dv._run_script(repo, "probe.py")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "1"


# =========================================================================================
# (d) — the per-alternative rows, and the `was:` field test (Ruling 102 §5)
# =========================================================================================

_CLEAN = {"docs/a.md": "a clean line with no legacy citation\n"}


def test_row_d_is_green_on_a_clean_corpus_and_red_on_one_planted_token(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """Red-then-green on the same predicate: one planted `NT-0001` flips the row."""
    control = {"docs/a.md": "see NT-0001 for the reasoning\n"}
    snap = _snapshot(dv, tmp_path / "green", _CLEAN, control)
    rows = _d_rows(dv, snap)
    assert rows["d1"].verdict == dv.PASS

    broken = {"docs/a.md": "a line that still says NT-0001\n"}
    snap2 = _snapshot(dv, tmp_path / "red", broken, control)
    rows2 = _d_rows(dv, snap2)
    assert rows2["d1"].verdict == dv.FAIL
    assert rows2["d1"].migrated.startswith("1 line")


def test_row_d_fails_when_its_control_is_zero(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """§7(d)'s `F-W[0-9]` case, generalised: a zero with a zero control proves nothing.

    Broken input here is a *control* in which the predicate never fired. The migrated tree
    is spotless — and the row must still be red, because a clean corpus and a dead
    predicate are indistinguishable from that figure alone.
    """
    snap = _snapshot(dv, tmp_path / "nocontrol", _CLEAN, _CLEAN)
    rows = _d_rows(dv, snap)
    assert rows["d1"].verdict == dv.FAIL
    assert "control is 0" in rows["d1"].note


def test_row_d_fails_over_an_empty_population(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """NT-0007: a green over a zero denominator is a fail, not a pass."""
    snap = _snapshot(dv, tmp_path / "empty", {"docs/a.md": ""}, {"docs/a.md": ""})
    rows = _d_rows(dv, snap)
    assert rows["d1"].verdict == dv.FAIL


# ---------------------------------------------------------------------------------------
# Rows (d9)-(d12), three framework defects found live 2026-09-05 in
# `_path_alternative_verdict`'s own "real moved file" test.
# ---------------------------------------------------------------------------------------

_REDIRECTS_HEADER = "old_id,new_id,old_path,new_path,citing_dir\n"


def test_path_alternative_ignores_a_same_path_redirect_row(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """A `docs/REDIRECTS.csv` row with `old_path == new_path` records a token rename
    made *inside* a file (`W1` -> `WK-954` inside `docs/roadmap.md`, which never moved),
    not a file move. Before this fix, `docs/roadmap.md` sitting anywhere in a match's
    two-line window flipped an unrelated, otherwise-disclosed citation to FATAL purely by
    proximity — found live against `docs/plans/2026-08-30-nt-0014-adoption.md`, a path no
    draft ever claims, sitting two rows above a genuine `docs/roadmap.md` mention in the
    same table.
    """
    migrated = {
        "docs/REDIRECTS.csv": _REDIRECTS_HEADER + "W1,WK-954,docs/roadmap.md,docs/roadmap.md,\n",
        "docs/a.md": (
            "| 19 | `docs/plans/2026-08-30-nt-0014-adoption.md` | New plan |\n"
            "| 20 | `docs/roadmap.md` | Amend |\n"
        ),
    }
    control = {"docs/a.md": "see docs/plans/2026- for background\n"}
    snap = _snapshot(dv, tmp_path, migrated, control)
    rows = _d_rows(dv, snap)
    assert rows["d9"].verdict != dv.FAIL, (
        "docs/roadmap.md's same-path redirect row must not make an unrelated "
        f"citation FATAL: {rows['d9'].note}"
    )


def test_path_alternative_excludes_a_split_source_index_file(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """RL-287/RL-255: a family split-source index's `` `was:` `` table column and
    "`<old>` became N documents." heading must keep naming the pre-migration path
    forever — there is no single successor to repoint a split source to. Before this
    fix, `docs/<family>/INDEX.md` (generated whole by `doc-id.py migrate`, matching this
    ruled shape everywhere in its body) was scanned like any other file and counted every
    row of its own ruled provenance as an unrepointed, fatal citation.
    """
    migrated = {
        "docs/REDIRECTS.csv": (
            _REDIRECTS_HEADER
            + "PL-100,PL-00100,docs/plans/2026-08-01-x.md,docs/plans/PL-00100-a.md,\n"
            + "RL-200,RL-00200,docs/plans/2026-08-01-x.md,docs/rulings/RL-00200-b.md,\n"
        ),
        "docs/rulings/INDEX.md": (
            "## 2026-08-01-x.md\n\n"
            "`docs/plans/2026-08-01-x.md` became 2 documents.\n\n"
            "| Document | Title | `was:` |\n"
            "|---|---|---|\n"
            "| [`RL-200`](RL-00200-b.md) | B | `docs/plans/2026-08-01-x.md` |\n"
        ),
    }
    control = {"docs/a.md": "see docs/plans/2026- for background\n"}
    snap = _snapshot(dv, tmp_path, migrated, control)
    rows = _d_rows(dv, snap)
    assert rows["d9"].verdict != dv.FAIL, rows["d9"].note


def test_path_alternative_excludes_a_vendored_skills_own_files(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """NT-0019 §1.5 / Ruling 69: a vendored skill's own files (never the manifest) are
    excluded from every migration action, citation rewrite included — "vendored files
    stay as upstream wrote them" (`CLAUDE.md` §12). A citation inside one can never be
    repointed by design, so it must not count toward this row's fatal population.
    """
    vendored_name = next(iter(dv._docid._VENDORED_SKILLS))
    migrated = {
        "docs/REDIRECTS.csv": (
            _REDIRECTS_HEADER
            + "PL-1,PL-00001,docs/plans/2026-08-01-x.md,docs/plans/PL-00001-a.md,\n"
        ),
        f".claude/skills/{vendored_name}/scripts/task-brief": (
            "# see docs/plans/2026-08-01-x.md for the house pattern\n"
        ),
    }
    control = {"docs/a.md": "see docs/plans/2026- for background\n"}
    snap = _snapshot(dv, tmp_path, migrated, control)
    rows = _d_rows(dv, snap)
    assert rows["d9"].verdict != dv.FAIL, rows["d9"].note


def test_was_exclusion_is_a_field_test_not_a_substring_test(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """Ruling 102 §5, as a corpus on which the two tests disagree.

    Three lines carry the token `docs/notes/`:

    * the front-matter `was:` field  — excluded (provenance, not a citation);
    * a prose line that merely contains the characters ``was:``  — **counted**; a
      substring test would have dropped it, and dropping exactly this class is what hid
      real hits on three of thirteen alternatives (handover §2);
    * a plain prose line  — counted.

    The field test therefore reports 2 and the substring test would report 1. The
    assertion is on the field test's answer.
    """
    doc = (
        "---\n"
        "family: proposal\n"
        "title: t\n"
        "status: draft\n"
        "owner: x\n"
        "was: docs/notes/0019-one-id-per-document.md\n"
        "---\n"
        "\n"
        "The `was:` field once pointed at docs/notes/0007-something.md and was wrong.\n"
        "See docs/notes/0003-duplicated-status-goes-stale.md.\n"
    )
    snap = _snapshot(dv, tmp_path / "wasfield", {"docs/a.md": doc}, {"docs/a.md": doc})
    corpus = dv.load_corpus(snap.migrated)
    lines, _files = corpus.scan(re.compile(r"\b(docs/notes/)"))
    # the `was:` *field* line is excluded; a prose line containing `was:` is not
    assert lines == 2
    # And the field itself is the one line excluded — named, not inferred.
    assert corpus.was_lines["docs/a.md"] == frozenset({5})


def test_was_field_line_numbers_ignores_a_was_key_outside_front_matter(
    dv: Any,
) -> None:
    """A `was:` inside a fenced example further down the file is not the field."""
    text = "---\nfamily: f\n---\n\n```yaml\nwas: docs/notes/x.md\n```\n"
    assert dv.was_field_line_numbers(text) == frozenset()


def test_disclosed_alternative_does_not_set_the_exit_code_but_still_reports(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """`\\bF[0-9]{2}\\b` is excluded from the zero requirement **with its count disclosed**.

    Control carries the same three values as migrated (never fewer) so this stays a pure
    disclosure proof: the 2026-09-04 ruling (`to-lead.md:1017`) makes a genuinely *new*
    value REGRESSION even for a disclosed class, and that is a different test
    (`test_disclosed_alternative_still_regresses_on_a_new_value` below).
    """
    migrated = {"docs/a.md": "F41 and F85 and F96\n"}
    control = {"docs/a.md": "F41 and F85 and F96, again\n"}
    snap = _snapshot(dv, tmp_path / "disc", migrated, control)
    rows = _d_rows(dv, snap)
    assert rows["d3"].verdict == dv.DISCLOSE
    assert rows["d3"].fatal is False
    assert rows["d3"].migrated.startswith("1 line")  # one *line*, three occurrences


def test_disclosed_alternative_still_regresses_on_a_new_value(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """The 2026-09-04 ruling (`to-lead.md:1017`), clause 1, applied to a `D_DISCLOSED`
    member other than (d8): "any such value is REGRESSION, disclosed class or not."
    `F96` in the migrated tree with no `F96` anywhere in control is a genuinely new bare
    finding-id value — fatal, even though the bare-`F` alias class is otherwise exempt
    from the zero requirement."""
    migrated = {"docs/a.md": "F41 and F96\n"}
    control = {"docs/a.md": "F41\n"}
    row = _d_rows(dv, _snapshot(dv, tmp_path / "disc-new", migrated, control))["d3"]
    assert row.verdict == dv.REGRESSION
    assert row.fatal
    assert "F96" in row.note


def test_d_alternatives_equals_the_shared_constant_not_a_private_copy(dv: Any) -> None:
    """Task 17, Ruling 67 §2: "(d) and check 36 are one rule at two times, so they read
    ONE." `D_ALTERNATIVES` reads `_docid.LEGACY_FORM_PATTERNS` — the identical tuple
    `audit-docs.py`'s check 36 reads, never a value retyped independently. Compared by
    `==`, not `is`: each fixture here loads `_docid.py` fresh under its own module name
    (`tests/test_doc_id_verify.py`'s own `_load_by_path` idiom, one instance per name), so
    even the correctly-consolidated tuples are two separate Python objects with equal
    content — `is` would fail for a reason that has nothing to do with the property this
    test exists to prove. A private, independently-retyped copy, even one with identical
    content today, silently diverges the next time either file edits its own — which is
    exactly what happened here before task 17 (this module's old `F-W[0-9]`/`NT-00` were
    already narrower than check 36's own forms; `==` catches that the moment it recurs,
    just as reliably as `is` would if the two really did share one object)."""
    docid = _load_by_path("_docid_for_shared_constant", ROOT / "scripts" / "_docid.py")
    assert dv.D_ALTERNATIVES == docid.LEGACY_FORM_PATTERNS
    assert len(dv.D_ALTERNATIVES) == 13
    audit_docs = _load_by_path(
        "_audit_docs_for_shared_constant", ROOT / "scripts" / "audit-docs.py"
    )
    assert audit_docs.LEGACY_FORM_PATTERNS == docid.LEGACY_FORM_PATTERNS


#: Ruling 67 §2 Part 1: "every alternative in (d) must match a COMPLETE legacy identifier
#: or path, never a proper prefix of one." Each entry's own bare-prefix broken form — the
#: text the alternative would still match if its Part 1 anchoring were dropped — paired
#: with a complete form it must match, so the anchoring each carries is proven rather than
#: assumed. Four labels are absent, each for a distinct, checked reason:
#: the five path entries carry no `\b` at all (a path has no "complete form" the way an id
#: token does); "ADR id" and "workstream/slice id" both use `[0-9]+`/`{3}`-shaped digit
#: runs whose bug is over-matching a PREFIX OF A LONGER token (fixed-width `{3}` for ADR;
#: greedy `[0-9]+` already consumes a whole longer run for workstream, so its own trailing
#: `\b` is not load-bearing the same way), never a bare-prefix self-match — "ADR id" has
#: its own dedicated proof,
#: `test_d6_anchor_does_not_trip_on_a_correctly_migrated_five_digit_id`.
_PART_1_SELF_MATCH_CASES: Final = (
    ("note id", "the NT-00 alternative", "NT-0019"),
    ("finding id (workstream form)", "see F-W11 here", "F-W11-1-3"),
    ("workflow id", "wf-01x", "wf-01"),
    ("ruling reference", "Ruling 6x", "Ruling 67"),
    ("scoped requirement id", "FR-RATE-1x", "FR-RATE-13"),
)


@pytest.mark.parametrize(("label", "broken", "complete"), _PART_1_SELF_MATCH_CASES)
def test_part_1_anchoring_rejects_the_bare_prefix_each_label_names(
    dv: Any, label: str, broken: str, complete: str
) -> None:
    """Ruling 67 §2 Part 1's own broken-input proof, per alternative: the anchored pattern
    must NOT fire on a bare prefix of its own shape — the defect the original `NT-00` had,
    self-matching NT-0019 §7's own defining sentence."""
    pattern = dict(dv.D_ALTERNATIVES)[label]
    assert not pattern.search(broken), f"{label}: {broken!r} must not match"
    assert pattern.search(complete), f"{label}: {complete!r} must match"


# =========================================================================================
# (g) — the token-boundary bug, with the record's own named broken input
# =========================================================================================


def test_mangled_citation_predicate_is_ruling_102s_named_broken_input(
    dv: Any,
) -> None:
    """Ruling 102 §2 row 1: *"`NFR-RATE-13/14` is the broken-input proof."*

    Red: the mangled form `NFR-775/14` — one real requirement and one meaningless
    fragment. Green: the intact compound `NFR-RATE-13/14`, which must **not** match, or
    the predicate would fire on every healthy compound citation in the corpus.
    """
    assert dv.MANGLED_CITATION_RE.search("close the owed list lost NFR-775/14 (F41)")
    assert not dv.MANGLED_CITATION_RE.search("close the owed list lost NFR-RATE-13/14 (F41)")
    # The at-risk population predicate is the mirror image.
    assert dv.COMPOUND_CITATION_RE.search("NFR-RATE-13/14")
    assert not dv.COMPOUND_CITATION_RE.search("NFR-775/14")


@pytest.mark.parametrize(
    "mangled",
    ["FR-723/48", "NFR-775/14", "OQ-814/16", "OQ-832/2", "OQ-907/2/3/5"],
)
def test_every_mangled_example_the_handover_recorded_is_caught(
    dv: Any, mangled: str
) -> None:
    """The five examples handover §3 printed. A predicate that misses one of the forms it
    was written from is a predicate nobody checked against its own evidence."""
    assert dv.MANGLED_CITATION_RE.search(f"see {mangled} for detail")


# =========================================================================================
# (g) g2 — row_g wraps `doc-id.classify_migration_diff`'s per-class breakdown into the
# Row, never reimplementing the six-class filter itself (Ruling 68 §3). A fake `docid`
# stands in for the real module so these tests pin row_g's OWN aggregation logic — which
# class counts get printed, which residue drives the verdict — independent of whether the
# classifier itself is correct, which `tests/test_doc_id_migrate.py`'s
# `test_acceptance_item_g_*` and `test_class6_*` tests already prove on the real fixture
# corpus and the real generators.
# =========================================================================================


class _FakeClassification:
    def __init__(
        self,
        per_class: dict[str, tuple[str, ...]],
        violations: tuple[str, ...],
        *,
        unchanged: int = 0,
    ) -> None:
        self.per_class = per_class
        self.violations = violations
        self.unchanged = unchanged

    @property
    def population(self) -> int:
        return sum(len(v) for v in self.per_class.values())


class _FakeDocid:
    """Every attribute `row_g` reads off the real `doc-id.py` module, and nothing else."""

    CLASSIFIED_BY_NONE = "classified-by-none"
    _RULING_68_CLASSES = (
        ("1-front-matter-stamp", "class 1"),
        ("2-reference-token", "class 2"),
        ("3-move", "class 3"),
        ("4-split", "class 4"),
        ("5-roadmap-restructure", "class 5"),
        ("6-generated-artifact", "class 6"),
    )

    def __init__(self, classification: _FakeClassification) -> None:
        self._classification = classification

    def classify_migration_diff(self, old_root: Any, new_root: Any) -> _FakeClassification:
        return self._classification


#: A compound citation the migration cannot safely rewrite is left exactly as it was
#: (Ruling 102 §2 row 1's own control) — the g1 sub-predicate exists to catch a *mangled*
#: rewrite, which this fixture deliberately does not exercise; g1 is proven red-then-green
#: on its own in `test_row_d_is_green_on_a_clean_corpus_and_red_on_one_planted_token`'s
#: sibling tests above.
_G_CLEAN_COMPOUND = {"docs/a.md": "see NFR-RATE-13/14 for the reasoning\n"}
_G_CLEAN_MIGRATED = dict(_G_CLEAN_COMPOUND)


def test_row_g_reports_every_class_count_separately_not_one_aggregate(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """Ruling 68 §3: "(g)'s filter is implemented as code with the six classes named."
    Every one of the six classes' counts must be individually readable off the row, plus
    the residue — never folded into a single pass/fail number.
    """
    snap = _snapshot(dv, tmp_path, _G_CLEAN_MIGRATED, _G_CLEAN_COMPOUND)
    classification = _FakeClassification(
        per_class={
            "1-front-matter-stamp": ("docs/x1.md",),
            "2-reference-token": ("docs/x2.md", "docs/x2b.md"),
            "3-move": ("docs/x3.md",),
            "4-split": (),
            "5-roadmap-restructure": ("docs/roadmap.md",),
            "6-generated-artifact": ("docs/INDEX.md",),
            "classified-by-none": (),
        },
        violations=(),
    )
    fake_docid = _FakeDocid(classification)
    mig = dv.load_corpus(snap.migrated)
    ctl = dv.load_corpus(snap.control)
    row = dv.row_g(fake_docid, snap, mig, ctl)

    assert row.verdict == dv.PASS
    for key in (
        "1-front-matter-stamp=1", "2-reference-token=2", "3-move=1", "4-split=0",
        "5-roadmap-restructure=1", "6-generated-artifact=1", "classified-by-none=0",
    ):
        assert key in row.migrated, row.migrated


def test_row_g_a_nonempty_residue_fails_and_names_the_violation(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """Ruling 68 §2: "A hunk the filter cannot classify fails; it is never passed
    through." One unclassified file must fail the row and name itself in the note, even
    though every other file is cleanly explained."""
    snap = _snapshot(dv, tmp_path, _G_CLEAN_MIGRATED, _G_CLEAN_COMPOUND)
    classification = _FakeClassification(
        per_class={
            "1-front-matter-stamp": ("docs/x1.md",),
            "2-reference-token": (),
            "3-move": (),
            "4-split": (),
            "5-roadmap-restructure": (),
            "6-generated-artifact": (),
            "classified-by-none": ("docs/rogue.md",),
        },
        violations=("docs/rogue.md: appeared with no REDIRECTS.csv row naming where it "
                    "came from",),
    )
    fake_docid = _FakeDocid(classification)
    mig = dv.load_corpus(snap.migrated)
    ctl = dv.load_corpus(snap.control)
    row = dv.row_g(fake_docid, snap, mig, ctl)

    assert row.verdict == dv.FAIL
    assert "docs/rogue.md" in row.note
    assert "classified-by-none=1" in row.migrated


def test_row_g_names_every_residue_hunk_never_truncates(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """W37-6 channel `:392`/`:403`: the deputy's advisory on #706 found the note used to
    truncate to five violations plus a "+N more" count — Ruling 68 §2 `:268`'s "a hunk the
    filter cannot classify fails; it is never passed through" was read by the deputy as
    obliging every hunk to be *named*, not summarised past the fifth. Seven unclassified
    files here, one more than the old truncation point, proves every one of the seven
    reaches the note and that no "+N more" placeholder survives in its place.
    """
    snap = _snapshot(dv, tmp_path, _G_CLEAN_MIGRATED, _G_CLEAN_COMPOUND)
    residue_files = tuple(f"docs/rogue{i}.md" for i in range(7))
    residue_violations = tuple(
        f"{rel}: appeared with no REDIRECTS.csv row naming where it came from"
        for rel in residue_files
    )
    classification = _FakeClassification(
        per_class={
            "1-front-matter-stamp": (),
            "2-reference-token": (),
            "3-move": (),
            "4-split": (),
            "5-roadmap-restructure": (),
            "6-generated-artifact": (),
            "classified-by-none": residue_files,
        },
        violations=residue_violations,
    )
    fake_docid = _FakeDocid(classification)
    mig = dv.load_corpus(snap.migrated)
    ctl = dv.load_corpus(snap.control)
    row = dv.row_g(fake_docid, snap, mig, ctl)

    assert row.verdict == dv.FAIL
    for rel in residue_files:
        assert rel in row.note, (rel, row.note)
    for violation in residue_violations:
        assert violation in row.note, (violation, row.note)
    assert "more" not in row.note, row.note
    assert "classified-by-none=7" in row.migrated


def test_row_g_note_leads_with_the_residue_cause_table(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """W37-6 channel `:512-536`: the deputy's ruling on the class-6 keying fix refused a
    bare residue total ("the 504 acted on as a total rather than per cause" is a named
    violation) and required `classified-by-none` printed *by cause*, with counts and three
    examples each (Ruling 102 §3's "name them"). Four residue members, one per named
    shape plus one that matches none, prove the table classifies each correctly, counts
    it, and still leads the full per-file listing rather than replacing it.
    """
    # Built by concatenation, not a literal path: this file is itself part of the tracked
    # corpus `tests/test_notes_move_citations.py::test_no_living_file_cites_the_old_notes_
    # path` scans, and a literal occurrence of the vacated notes root would flag this file
    # as a living citation of it — the identical defence that check's own module uses on
    # itself.
    notes_stub = ".claude" + "/" + "notes" + "/0099-a-stub.md"
    control = dict(_G_CLEAN_COMPOUND)
    control[notes_stub] = (
        "# Moved\n\nThis note moved to [`docs/rfcs/RFC-00099-x.md`]"
        "(../../docs/rfcs/RFC-00099-x.md) on 2026-09-01 (RFC-181 Slice 4).\n"
    )
    control[".claude/skills/example-skill/SKILL.md"] = (
        "---\nname: example-skill\ndescription: x\n---\nBody citing FR-1.\n"
    )
    control["docs/plans/example-range.md"] = "Cites FR-PLAT-1..4 in prose.\n"
    control["docs/specs/example-mystery.md"] = "An ordinary line, no citation shape.\n"
    migrated = dict(_G_CLEAN_MIGRATED)

    snap = _snapshot(dv, tmp_path, migrated, control)
    residue_files = (
        notes_stub,
        ".claude/skills/example-skill/SKILL.md",
        "docs/plans/example-range.md",
        "docs/specs/example-mystery.md",
    )
    classification = _FakeClassification(
        per_class={
            "1-front-matter-stamp": (),
            "2-reference-token": (),
            "3-move": (),
            "4-split": (),
            "5-roadmap-restructure": (),
            "6-generated-artifact": (),
            "classified-by-none": residue_files,
        },
        violations=tuple(
            f"{rel}: appeared with no REDIRECTS.csv row naming where it came from"
            for rel in residue_files
        ),
    )
    fake_docid = _FakeDocid(classification)
    mig = dv.load_corpus(snap.migrated)
    ctl = dv.load_corpus(snap.control)
    row = dv.row_g(fake_docid, snap, mig, ctl)

    assert row.verdict == dv.FAIL
    table, _sep, listing = row.note.partition(" || ")
    assert table.startswith("residue by cause:")
    assert "cause2b-notes-stub-relative-link=1" in table
    assert notes_stub in table
    assert "cause1-foreign-frontmatter=1" in table
    assert ".claude/skills/example-skill/SKILL.md" in table
    assert "cause2a-range-citation=1" in table
    assert "docs/plans/example-range.md" in table
    assert "other=1" in table
    assert "docs/specs/example-mystery.md" in table
    # The full per-file listing (already covered above) still follows, unshortened.
    for rel in residue_files:
        assert rel in listing


def test_residue_cause_precedence_and_slash_compound_shape(dv: Any) -> None:
    """`_residue_cause`'s own fixed check order and its one reported-not-investigated
    shape (W37-6 channel `:512-536`'s cause 2b footnote): a notes-stub path is decided by
    path alone before any content is read; a foreign-frontmatter file is decided before
    its body is checked for a citation shape; a 3+-part slash chain
    (`FR-RATE-56/57/58`, found investigating 2b, not one of the deputy's three named
    causes) is reported under its own label rather than folded into `other`.
    """
    notes_stub = ".claude" + "/" + "notes" + "/0001-x.md"
    assert dv._residue_cause(notes_stub, None) == "cause2b-notes-stub-relative-link"
    assert dv._residue_cause(
        ".claude/skills/x/SKILL.md", ("---", "name: x", "---", "Cites FR-PLAT-1..4.")
    ) == "cause1-foreign-frontmatter"
    assert dv._residue_cause(
        "docs/plans/x.md", ("Cites the range FR-PLAT-1..4 in prose.",)
    ) == "cause2a-range-citation"
    assert dv._residue_cause(
        "backend/src/app/errors.py", ("# refs FR-RATE-56/57/58",)
    ) == "slash-compound-citation (unassigned — reported, not investigated)"
    assert dv._residue_cause("docs/specs/x.md", ("nothing of interest",)) == "other"
    assert dv._residue_cause("docs/specs/x.md", None) == "other"


def test_residue_cause3_legacy_path_citation(dv: Any) -> None:
    """cause3 (this executor's `docs/` sample, six of ten files, W37-6 channel `:770`'s
    `docs/`-tree triage): a prose citation to another document by its pre-migration
    relative path — `docs/notes/...`, `docs/audit/...`, `docs/plans/2026-...` — fails
    DP-7's inverse because `redirects_inverse` is built only from `REDIRECTS.csv`'s id
    columns, never from a citation's own literal path string. Reuses
    `_docid.LEGACY_FORM_PATTERNS`' five `"...path"` entries rather than a new pattern.
    Broken-input proof against the actual shapes read in `docs/process/delivery-
    process.md` and `docs/audit/findings/F27.md`: each of the five legacy-path forms
    fires, and a citation outside all five (`docs/README.md`'s own residual shape —
    `workflows/wf-01-dataset-to-model.md`, a bare relative path with no `docs/` prefix)
    does not, falling through to `other` as documented rather than mis-firing.
    """
    assert dv._residue_cause(
        "docs/process/delivery-process.md",
        ("Adopted 2026-08-29 from NT-0010 (`docs/notes/0010-layered-slice-based-"
         "workflow.md`),",),
    ) == "cause3-legacy-path-citation"
    assert dv._residue_cause(
        "docs/audit/findings/F27.md",
        ("**Register row:** `docs/audit/register.md`, the row self-naming `(F27)`.",),
    ) == "cause3-legacy-path-citation"
    assert dv._residue_cause(
        "docs/research/x.md",
        ("named in `docs/plans/2026-08-29-w11-1-evaluator-core.md`:",),
    ) == "cause3-legacy-path-citation"
    assert dv._residue_cause(
        "docs/README.md",
        ("2. `workflows/wf-01-dataset-to-model.md` — the shortest end-to-end story.",),
    ) == "other"


def test_residue_cause4_compound_token_adjacent_uppercase(dv: Any) -> None:
    """cause4 (this executor's `docs/` sample, `docs/contracts/schemas/job.schema.json`):
    a genuine forward-migration corruption, not an inverse gap — `doc-id.py`'s
    `_compound_token_re` (`\\b{tok}((?:[-/]\\d+)*)`) has no trailing `\\b`, so a legacy
    work token (`W3`) matches as a bare prefix of any longer run of word characters
    starting the same way, e.g. `W3C` (the web-standards body, unrelated to this
    repository's `W`-family ids) comes out `WK-944C`. `_WORK_FAMILY_TOKEN_RE`'s own
    suffix group is lowercase-only (`[a-z]?`), so an uppercase letter can never
    legitimately continue a work id — `\\bW[0-9]+[A-Z]` is a precise proxy for the
    pre-migration shape that triggers the bug. Broken-input proof against the actual line
    read in `job.schema.json` (`"description": "W3C/OpenTelemetry trace id..."`), plus a
    negative control: a legitimate lowercase work-slice suffix (`W6a`) must not fire this
    cause, since that shape is not the bug's trigger.
    """
    assert dv._residue_cause(
        "docs/contracts/schemas/job.schema.json",
        ('          "description": "W3C/OpenTelemetry trace id: 32 lowercase hex '
         'characters (00 §5.3)."',),
    ) == "cause4-compound-token-adjacent-uppercase"
    assert dv._residue_cause(
        "docs/plans/x.md", ("zero callers since W6a; this slice gives it its caller.",)
    ) != "cause4-compound-token-adjacent-uppercase"


def test_residue_cause_third_scope_shapes(dv: Any) -> None:
    """W37-6's third `other`-triage scope (everything not under `docs/`, `tests/`,
    `backend/`, `frontend/`, `scripts/`, `packages/`): two shapes found sampling that
    remainder whole (14 members) rather than by ten-sample, each reported by the same
    convention as the slash-compound shape above — named, counted, not fixed. Each
    assertion pairs a positive with the narrowest broken input that must NOT trigger it,
    so the check is falsifiable rather than merely illustrative.

    A third candidate this executor found on the same scope (an id token and its
    `docs/plans/` or `docs/notes/` path rewritten together, e.g. a markdown link) turned
    out to be cause3 — `test_residue_cause3_legacy_path_citation` above — read one level
    more generally by the sibling `docs/`-triage executor; the assertion just below proves
    that convergence rather than re-introducing a second label for it.
    """
    # The "id+path compound" candidate resolves to cause3, not a new label: cause3's
    # `_LEGACY_PATH_RES` matches on the bare path alone, so it claims this line before any
    # id-plus-path check would get a chance to.
    assert dv._residue_cause(
        "CLAUDE.md",
        ("See [`NT-0003`](docs/notes/0003-duplicated-status-goes-stale.md).",),
    ) == "cause3-legacy-path-citation"

    # new-frontmatter-stamp-no-move: no leading `---` before migration, a full block
    # (starting `family:`) stamped in after, at the same path (no move). A file that
    # already had `---` (cause 1's territory) must not match even with new_lines matching
    # the block shape; a file with new_lines absent (no migrated read available) must fall
    # through rather than raise.
    assert dv._residue_cause(
        ".claude/roles/executor.md",
        ("# executor", "", "- some body line"),
        ("---", "family: reference", "title: executor", "status: active", "---", "", "# executor"),
    ) == "new-frontmatter-stamp-no-move (unassigned — reported, not investigated)"
    assert dv._residue_cause(
        ".claude/skills/x/SKILL.md",
        ("---", "name: x", "---", "Body."),
        ("---", "family: reference", "---", "Body."),
    ) == "cause1-foreign-frontmatter"  # existing block: cause 1 owns this, not the new check
    assert dv._residue_cause(
        ".claude/roles/executor.md", ("# executor", "- some body line"), None
    ) == "other"  # no migrated read available: falls through, does not raise

    # unmapped-work-slice-key: a `W<n>[a-z]?-<m>` slice key on the pre-migration line —
    # the deputy's own unmapped-tokens ruling already names this shape (`W<n>-<m>`); this
    # only reports that it also surfaces as (g) residue. A plain requirement id must not
    # match it.
    assert dv._residue_cause(
        "examples/fremtpl2/seed.py", ("# no identity (W6b-10) and no workspace (W6b-11)",)
    ) == "unmapped-work-slice-key (named elsewhere, reported here by shape)"
    assert dv._residue_cause(
        "docs/specs/x.md", ("Cites FR-PLAT-37 in prose.",)
    ) == "other"


def test_residue_cause5_fixture_corpus(dv: Any) -> None:
    """cause5 (code-tree triage, W37-6 channel `:599`'s dispatch): `tests/fixtures/
    docs-ids/**` and `tests/fixtures/docs-migration/**` are synthetic corpora built to
    test `doc-id.py` itself, holding deliberately old-form ids as test data — decided by
    path alone, content irrelevant, the same "path is conclusive" rule `_NOTES_STUB_RE`
    already uses. A file merely *adjacent* to one of these directories (sharing its
    prefix as a substring but not contained in it) must not fire.
    """
    assert (
        dv._residue_cause("tests/fixtures/docs-ids/w37-3-corpus/roadmap.md", None)
        == "cause5-fixture-corpus-old-form-ids"
    )
    assert (
        dv._residue_cause(
            "tests/fixtures/docs-migration/docs/roadmap.md", ("anything",)
        )
        == "cause5-fixture-corpus-old-form-ids"
    )
    assert dv._residue_cause("tests/fixtures/docs-ids-other/x.md", ("anything",)) != (
        "cause5-fixture-corpus-old-form-ids"
    )


def test_residue_cause6_pycache_build_artifact(dv: Any) -> None:
    """cause6 (code-tree triage): `scripts/__pycache__/*.pyc` — compiled bytecode the
    verify snapshot's own tree walk should never have included. Binary, so `old_lines` is
    `None`; checked by path alone before the `old_lines is None -> "other"` fallback
    would otherwise catch it.
    """
    assert (
        dv._residue_cause("scripts/__pycache__/_docid.cpython-312.pyc", None)
        == "cause6-pycache-build-artifact"
    )
    assert dv._residue_cause("scripts/doc-id.py", None) == "other"


def test_row_g_empty_classified_population_fails(dv: Any, tmp_path: pathlib.Path) -> None:
    """NT-0007: a green over an empty population is a fail, not a pass — g2's population
    is the file count `classify_migration_diff` classified, not the corpus size."""
    snap = _snapshot(dv, tmp_path, _G_CLEAN_MIGRATED, _G_CLEAN_COMPOUND)
    empty_per_class: dict[str, tuple[str, ...]] = {
        key: () for key, _ in _FakeDocid._RULING_68_CLASSES
    }
    empty_per_class["classified-by-none"] = ()
    classification = _FakeClassification(per_class=empty_per_class, violations=())
    fake_docid = _FakeDocid(classification)
    mig = dv.load_corpus(snap.migrated)
    ctl = dv.load_corpus(snap.control)
    row = dv.row_g(fake_docid, snap, mig, ctl)

    assert row.verdict == dv.FAIL
    assert "empty population" in row.note


# =========================================================================================
# (h2) — the vacuous pass, which is the failure mode that reads as a success
# =========================================================================================


def test_vacuity_probes_read_the_lines_audit_docs_actually_prints(
    dv: Any,
) -> None:
    """Red: the migrated tree's own summary, verbatim from handover §4 — every denominator
    zero. Green: the control's. The probes must extract both, or the vacuous-pass rule has
    nothing to compare."""
    migrated_out = (
        "  0 requirements defined across 8 specs\n"
        "  0 open questions, all mirrored\n"
        "  journey citations: 0 endpoints, 0 functions, all declared\n"
        "  0 of 0 §10 mirror rows carry their register status\n"
        "  check 37: 1 document(s) checked in scope, 0 exempt as verbatim-migrated "
        "(`was:`), 1 shape-checked\n"
    )
    control_out = (
        "  533 requirements defined across 8 specs\n"
        "  118 open questions, all mirrored\n"
        "  journey citations: 31 endpoints, 12 functions, all declared\n"
        "  118 of 118 §10 mirror rows carry their register status\n"
        "  check 37: 292 document(s) checked in scope, 292 exempt as verbatim-migrated "
        "(`was:`), 1 shape-checked\n"
    )
    mig = dv._probe_summary(migrated_out)
    ctl = dv._probe_summary(control_out)
    assert mig["requirements defined"] == 0
    assert ctl["requirements defined"] == 533
    assert mig["§10 mirror rows"] == 0
    assert ctl["§10 mirror rows"] == 118
    assert mig["check 37 `was:` exemptions"] == 0
    assert ctl["check 37 `was:` exemptions"] == 292
    vacuous = [k for k in mig if (ctl[k] or 0) > 0 and (mig[k] or 0) == 0]
    assert "requirements defined" in vacuous
    # Green half: an unchanged pair is not reported as vacuous.
    same = dv._probe_summary(control_out)
    assert [k for k in same if (ctl[k] or 0) > 0 and (same[k] or 0) == 0] == []


# =========================================================================================
# (e) and (f) — the two-reading rows stay red until the decision-maker rules
# =========================================================================================


def _index(ids: str) -> str:
    """A minimal `docs/INDEX.md` carrying `ids` — conjunct 3's authority."""
    return f"# Index\n\n{ids}\n"


def test_row_e_conjunct_3_excuses_a_token_that_resolves_to_nothing(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """Ruling 103 conjunct 3: a padded token that resolves to nothing is a **specimen of
    the form**, not a citation. Red-then-green on one corpus: the same line is a violation
    when `docs/INDEX.md` carries the id and a specimen when it does not."""
    doc = {"docs/a.md": "the rule is stated for PL-09998 in prose\n"}
    with_id = dict(doc, **{"docs/INDEX.md": _index("PL-9998 something")})
    without = dict(doc, **{"docs/INDEX.md": _index("PL-9997 something else")})
    snap = _snapshot(dv, tmp_path / "e3a", with_id, with_id)
    assert dv.row_e(dv.load_corpus(snap.migrated), dv.load_corpus(snap.control),
                    snap).verdict == dv.FAIL
    snap2 = _snapshot(dv, tmp_path / "e3b", without, without)
    assert dv.row_e(dv.load_corpus(snap2.migrated), dv.load_corpus(snap2.control),
                    snap2).verdict == dv.PASS


def test_row_e_conjunct_3_fails_loudly_when_the_index_resolves_nothing(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """An empty index would excuse **every** token as a specimen — a green over an authority
    that carries nothing (NT-0007). It must fail rather than pass."""
    doc = {"docs/a.md": "PL-09998 in prose\n", "docs/INDEX.md": "# Index\n"}
    snap = _snapshot(dv, tmp_path / "e3c", doc, doc)
    row = dv.row_e(dv.load_corpus(snap.migrated), dv.load_corpus(snap.control), snap)
    assert row.verdict == dv.FAIL
    assert "no authority" in row.note


def test_row_e_conjunct_0_excludes_a_fenced_block(dv: Any, tmp_path: pathlib.Path) -> None:
    """Ruled by the decision-maker: without a fence rule, a record documenting a padding
    defect must corrupt its own evidence to pass the lint. Red-then-green on the same token
    — a violation in prose, evidence inside a fence."""
    idx = _index("PL-9998")
    prose = {"docs/a.md": "PL-09998 in prose\n", "docs/INDEX.md": idx}
    fenced = {"docs/a.md": "```\nPL-09998 quoted as evidence\n```\n", "docs/INDEX.md": idx}
    s1 = _snapshot(dv, tmp_path / "e0a", prose, prose)
    assert dv.row_e(dv.load_corpus(s1.migrated), dv.load_corpus(s1.control),
                    s1).verdict == dv.FAIL
    s2 = _snapshot(dv, tmp_path / "e0b", fenced, fenced)
    assert dv.row_e(dv.load_corpus(s2.migrated), dv.load_corpus(s2.control),
                    s2).verdict == dv.PASS


def test_row_e_conjunct_2_strips_markdown_emphasis_before_the_path_test(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """Ruling 103 defect 3, as its own broken-input proof. A padded id inside a path, with
    bold markers splitting the token, is still a path — and before the stripping step the
    path test never saw one. The emphasised form must be excused; only the bare prose token
    is a violation."""
    # `RL-09999` rather than a real id, and this is not cosmetic: the first draft reused a
    # padded id that really resolves, and because this file is INSIDE the corpus row (e)
    # scans, the deliberately
    # violating fixture below became a genuine violation of the real corpus — the instrument
    # counting its own test, the same class as the (d11) floor task 17 removed. The number
    # is above every allocated id, so conjunct 3 excuses it there while this test supplies
    # its own `docs/INDEX.md` and still discriminates. Verified at the migrated tree:
    # `grep -c 'RL-9999\b' docs/INDEX.md` -> 0, highest allocated 1128.
    idx = _index("RL-9999")
    emphasised = {
        "docs/a.md": "see `docs/rulings/**RL-09999**-q5-file.md` for it\n",
        "docs/INDEX.md": idx,
    }
    s = _snapshot(dv, tmp_path / "e2a", emphasised, emphasised)
    assert dv.row_e(dv.load_corpus(s.migrated), dv.load_corpus(s.control),
                    s).verdict == dv.PASS
    bare = {"docs/a.md": "the pair was relayed as RL-09999\n", "docs/INDEX.md": idx}
    s2 = _snapshot(dv, tmp_path / "e2b", bare, bare)
    assert dv.row_e(dv.load_corpus(s2.migrated), dv.load_corpus(s2.control),
                    s2).verdict == dv.FAIL


def test_row_e_conjunct_2_strips_a_trailing_line_locator_before_the_path_test(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """A fourth predicate defect row (e)'s own measurement found, alongside Ruling 103's
    three: this corpus's own same-directory citation convention — `filename.md:123` or
    `filename.md:401-404`, no leading `docs/plans/` because both files share a directory —
    is a filename token per rule 3's own wording ("the leading component of a filename
    ending `.md`"), but the trailing `:<line>` defeated the bare `\\.[A-Za-z0-9]{2,4}$`
    extension test, which requires the token to *end* at the extension. Found on three real
    citations at `e97b97a` (`PL-92`, `PL-134`, `PL-142` each citing a sibling plan's old
    filename by `:<line>` — unpadded here, a citation rather than a specimen, per rule 2).
    Red-then-green on the identical padded id: bare in prose is
    still a violation; the same id leading a `filename.md:<line>` token, single line or a
    range, is a path."""
    idx = _index("PL-9998")
    bare = {
        "docs/a.md": "the pair was relayed as PL-09998 in the review\n",
        "docs/INDEX.md": idx,
    }
    s1 = _snapshot(dv, tmp_path / "e2c", bare, bare)
    assert dv.row_e(dv.load_corpus(s1.migrated), dv.load_corpus(s1.control),
                    s1).verdict == dv.FAIL

    single_line = {
        "docs/a.md": "see `PL-09998-slug.md:430` for the source\n",
        "docs/INDEX.md": idx,
    }
    s2 = _snapshot(dv, tmp_path / "e2d", single_line, single_line)
    assert dv.row_e(dv.load_corpus(s2.migrated), dv.load_corpus(s2.control),
                    s2).verdict == dv.PASS

    line_range = {
        "docs/a.md": "see `PL-09998-slug.md:401-404` for the source\n",
        "docs/INDEX.md": idx,
    }
    s3 = _snapshot(dv, tmp_path / "e2e", line_range, line_range)
    assert dv.row_e(dv.load_corpus(s3.migrated), dv.load_corpus(s3.control),
                    s3).verdict == dv.PASS


def test_row_e_conjunct_1_reads_pad_width_from_the_symbol(dv: Any) -> None:
    """Ruling 103 defect 1, and the reason `CLAUDE.md` §13 forbids a pasted constant: on
    one corpus `-0\\d{4}` and `-0[0-9]{3,4}` differed by **355 occurrences**, which is
    F85's shape inside an acceptance predicate."""
    assert str(_docid_pad_width(dv) - 1) in dv._PADDED_ID_RE.pattern
    assert dv._PADDED_ID_RE.search("PL-09998")
    # One digit short and one digit long must BOTH miss — the width is exact, not a floor.
    assert not dv._PADDED_ID_RE.search(" PL-0999 ")
    assert not dv._PADDED_ID_RE.search(" PL-099980 ")


def _docid_pad_width(dv: Any) -> int:
    """`_docid.PAD_WIDTH`, reached through the module under test rather than imported.

    `scripts/_docid.py` is loaded by path (its directory is on `sys.path` at runtime but is
    not a package mypy can resolve), so a direct `import _docid` here type-checks as a
    missing module. Going through `_docverify`'s own reference keeps one source for the
    width, which is the point of the conjunct being by symbol at all.
    """
    return int(_load_by_path("_docid_for_width", ROOT / "scripts" / "_docid.py").PAD_WIDTH)


def test_row_f_conjunct_2_discloses_a_split_source_instead_of_failing_on_it(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """Ruling 103's amendment. A split source's 3 occurrences leave one file and arrive in
    two; `REDIRECTS.csv` is one-to-one and names only one of them, so a naive per-file
    comparison reports three disagreements. They **close** — the residual is zero — so the
    conjunct passes with them disclosed."""
    control = {"docs/src.md": "VR-DST-1 a\nVR-DST-1 b\nVR-DST-1 c\n"}
    migrated = {
        "docs/one.md": "VR-DST-1 a\nVR-DST-1 b\n",
        "docs/two.md": "VR-DST-1 c\n",
        "docs/REDIRECTS.csv": "old_id,new_id,old_path,new_path\n"
                              "X,Y,docs/src.md,docs/one.md\n",
    }
    snap = _snapshot(dv, tmp_path / "f2", migrated, control)
    row = dv.row_f(dv.load_corpus(snap.migrated), dv.load_corpus(snap.control), None, snap)
    assert row.verdict == dv.PASS
    assert "disclosed split-source" in row.note
    assert "NAMED LIMITATION" in row.note


def test_row_f_fails_when_an_identifier_leaves_without_arriving(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """The residual is what makes conjunct 2 a test rather than a disclosure: a genuine
    loss does not close."""
    control = {"docs/src.md": "VR-DST-1 a\nVR-DST-1 b\nVR-DST-1 c\n"}
    migrated = {"docs/one.md": "VR-DST-1 a\n",
                "docs/REDIRECTS.csv": "old_id,new_id,old_path,new_path\n"
                                      "X,Y,docs/src.md,docs/one.md\n"}
    snap = _snapshot(dv, tmp_path / "f3", migrated, control)
    row = dv.row_f(dv.load_corpus(snap.migrated), dv.load_corpus(snap.control), None, snap)
    assert row.verdict == dv.FAIL
    assert "conjunct 1" in row.note  # the total moved, which conjunct 1 catches first


def test_row_f_conjunct_1_alone_would_have_passed_the_real_corpus(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """Why the strengthening earned its keep: totals equal, files moved. Conjunct 1 sees
    nothing; conjunct 2 is what looks."""
    control = {"docs/src.md": "VR-DST-1 a\nVR-DST-1 b\n"}
    migrated = {"docs/one.md": "VR-DST-1 a\n", "docs/two.md": "VR-DST-1 b\n"}
    snap = _snapshot(dv, tmp_path / "f1", migrated, control)
    mig, ctl = dv.load_corpus(snap.migrated), dv.load_corpus(snap.control)
    assert dv._per_file(mig, dv._VR_DST_RE) != dv._per_file(ctl, dv._VR_DST_RE)
    assert sum(dv._per_file(mig, dv._VR_DST_RE).values()) == sum(
        dv._per_file(ctl, dv._VR_DST_RE).values()
    )


def test_row_f_excludes_generated_paths_by_the_runs_own_list_not_a_literal_path(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """Ruling 105 D3 / #18 §1's own broken-input proof: *"move one VR-DST-1 from a governed
    body into another governed body → red; add a generated file quoting one → still
    green."* `generated_paths` is the run's own list (`MigrateResult.generated_paths`),
    never a hard-coded `docs/INDEX.md` check — a file at any path in that list is excluded,
    one NOT in it is not, however INDEX.md-shaped its name looks."""
    control = {"docs/src.md": "VR-DST-1 a\n"}
    # Red: a real move, no generated file involved — conjunct 1 must still catch a loss.
    moved_only = {"docs/dest.md": "VR-DST-1 a\n"}
    snap_red = _snapshot(dv, tmp_path / "f4red", moved_only, control)
    row_red = dv.row_f(
        dv.load_corpus(snap_red.migrated), dv.load_corpus(snap_red.control), None,
        snap_red, ("docs/dest.md",),
    )
    assert row_red.verdict == dv.FAIL, (
        "excluding the ONLY carrier of a real move must not manufacture a false green"
    )

    # Green: the identifier stays exactly where it was AND a generated file (arbitrarily
    # named, not "docs/INDEX.md") echoes it — the echo must not count as a new occurrence.
    with_generated_echo = {
        "docs/src.md": "VR-DST-1 a\n",
        "docs/some-other-generated.md": "VR-DST-1 a\n",
    }
    snap_green = _snapshot(dv, tmp_path / "f4green", with_generated_echo, control)
    row_green = dv.row_f(
        dv.load_corpus(snap_green.migrated), dv.load_corpus(snap_green.control), None,
        snap_green, ("docs/some-other-generated.md",),
    )
    assert row_green.verdict == dv.PASS
    assert "GENERATED, excluded" in row_green.note
    assert "docs/some-other-generated.md=1" in row_green.note

    # The default (no generated_paths passed) excludes nothing — existing callers unaffected.
    row_default = dv.row_f(
        dv.load_corpus(snap_green.migrated), dv.load_corpus(snap_green.control), None,
        snap_green,
    )
    assert row_default.verdict == dv.FAIL
    assert "GENERATED, excluded" not in row_default.note


# =========================================================================================
# Task 17 — (d) reads `_docid.LEGACY_FORM_PATTERNS`, the one constant Ruling 67 §2 shares
# with `audit-docs.py` check 36, never a private decomposition of a retyped sentence.
# =========================================================================================


def test_the_shared_constant_reproduces_the_hand_written_label_and_pattern_list(
    dv: Any,
) -> None:
    """Pins the thirteen `(label, pattern)` entries `_docid.LEGACY_FORM_PATTERNS` carries,
    so a change to the shared constant is visible here rather than only in whichever row
    or check happens to move. Every id-shaped entry's own Part 1 anchoring is asserted
    separately, by behaviour, in the `test_part_1_anchoring_rejects_the_bare_prefix_...`
    tests below."""
    expected_labels = (
        "note id", "finding id (workstream form)", "finding id (bare form)", "workflow id",
        "ruling reference", "ADR id", "scoped requirement id", "workstream/slice id",
        "legacy dated-plan path", "legacy audit path", "legacy notes path", "legacy adr path",
        "legacy claude-notes path",
    )
    assert tuple(label for label, _pattern in dv.D_ALTERNATIVES) == expected_labels
    assert len(dv.D_ALTERNATIVES) == 13


def test_a_mutated_constant_moves_both_docverify_and_check_36_the_same_way(
    dv: Any, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ruling 67 §2's own broken-input proof: *"change one alternative in the constant and
    both check 36 and the (d) rows move together; leave either reading a private copy and
    the test fails."* Fed the identical mutated tuple — the one shared constant's whole
    point is that a real edit to `_docid.py`'s source reaches both readers at their next
    import, which this proves by construction: the same mutation applied to what each
    reader is handed produces the same before/after shift in each."""
    audit_docs = _load_by_path(
        "_audit_docs_for_mutation_proof", ROOT / "scripts" / "audit-docs.py"
    )
    original = dv.D_ALTERNATIVES
    assert original == audit_docs.LEGACY_FORM_PATTERNS
    mutated = tuple(
        (label, re.compile(r"\bXX-MUTATED-\d+\b")) if label == "ADR id" else (label, pattern)
        for label, pattern in original
    )

    doc = "cites ADR-0004 in prose\n"
    snap = _snapshot(dv, tmp_path / "mut", {"docs/a.md": doc}, {"docs/a.md": doc})
    mig, ctl = dv.load_corpus(snap.migrated), dv.load_corpus(snap.control)

    before_rows = {r.key: r for r in dv.rows_d(mig, ctl)}
    adr_key_before = next(k for k, r in before_rows.items() if "ADR id" in r.title)
    assert not before_rows[adr_key_before].migrated.startswith("0 line")

    fixture_path = tmp_path / "a.md"
    fixture_path.write_text(doc, encoding="utf-8")
    before_sweep = audit_docs.sweep_legacy_forms([fixture_path], repo_root=tmp_path)
    assert any("ADR id" in hit for hit in before_sweep)

    monkeypatch.setattr(dv, "D_ALTERNATIVES", mutated)
    after_rows = {r.key: r for r in dv.rows_d(mig, ctl)}
    assert after_rows[adr_key_before].migrated.startswith("0 line"), (
        "the mutated pattern must no longer match ADR-0004"
    )

    after_sweep = audit_docs.sweep_legacy_forms(
        [fixture_path], repo_root=tmp_path, patterns=mutated
    )
    assert not any("ADR id" in hit for hit in after_sweep), (
        "check 36, fed the identical mutation, must move the same way"
    )


def test_padded_id_in_path_context_is_distinguished_from_prose(
    dv: Any,
) -> None:
    """The path-context rule on the markdown-link form.

    `[PL-09998-slug](docs/plans/PL-09998-slug.md)` carries the id twice. The **target** is
    unambiguously a path and is excluded. The **link text** is a bare slug with no `/` and
    no extension, so the enclosing-token rule counts it — the larger, conservative reading.
    That residual judgement is exactly why row (e) is `UNDETERMINED` rather than scored:
    Ruling 102 §2 row 5 gives the choice to the decision-maker, and an instrument that
    quietly picked the smaller number would be making it.
    """
    line = "[PL-09998-slug](docs/plans/PL-09998-slug.md) and bare PL-09998 in a sentence"
    hits = list(dv._PADDED_ID_RE.finditer(line))
    assert len(hits) == 3
    prose = [h for h in hits if not dv._in_path_context(line, h.start(), h.end())]
    # the link *target* is path context; the link text and the bare id are not
    assert len(prose) == 2
    assert line[prose[-1].start():prose[-1].end()] == "PL-09998"


def test_in_path_context_widens_past_an_angle_bracket_slug_placeholder(dv: Any) -> None:
    """A real corpus shape: NT-0019 §1.1 rule 3's own illustrative filename (and every
    `docs/_templates/*.md` copy-target line) writes the slug segment as an angle-bracket
    placeholder — `PL-01240-<slug>.md` — rather than a real word.

    `_TOKEN_BOUNDARY_RE` used to include `<` and `>`, so the right-side token walk
    stopped at the placeholder's opening `<` — one character short of ever reaching
    `.md` — and read the enclosing token as `PL-01240-`, which has no `/` and does not
    end in an extension: a real filename citation misclassified as prose. Removing `<`/`>`
    from the boundary class widens the walk past the placeholder to the actual extension.
    """
    line = "Filenames pad the integer: `PL-01240-<slug>.md`. Padding exists so `ls` sorts."
    hit = next(dv._PADDED_ID_RE.finditer(line))
    assert dv._in_path_context(line, hit.start(), hit.end())


def test_padded_hits_seq_disambiguates_two_occurrences_on_one_line(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """Two occurrences of the same padded id on one line, one path-shaped and one bare —
    `document-ids.md`'s own rule-3 sentence does exactly this: a filename exhibit
    (`PL-01245-widget.md`) followed later on the same line by the bare equivalence-list
    id (`PL-01245`).

    Conjunct 2's classification loop used to re-locate a match in the cleaned line by
    *text* (`m.group(0) == hit.token`) and take the first same-text match's path-context
    verdict for every hit sharing that text — so the bare occurrence inherited the
    filename occurrence's TRUE verdict and was wrongly excused: a false negative that
    suppresses a real violation. `PaddedHit.seq` (this hit's own ordinal among same-line
    matches) fixes it by re-locating each hit by its own position instead.
    """
    line = "See `PL-01245-widget.md` and also bare PL-01245 in the same sentence.\n"
    tree = _mkrepo(tmp_path / "t", {
        "docs/a.md": line,
        "docs/INDEX.md": "PL-1245\n",
    })
    corpus = dv.load_corpus(tree)
    resolvable = dv.index_ids(tree)
    assert "PL-1245" in resolvable
    _total, _after_corpus, after_path, after_index = dv.padded_hits(corpus, resolvable)
    # both occurrences survive conjunct 0 (neither fenced nor a `was:` line); only the
    # BARE one should survive conjunct 2 (not path-shaped)
    assert len(after_path) == 1
    assert after_path[0].line.rstrip().endswith("PL-01245 in the same sentence.")
    # and it resolves, so conjunct 3 must count it as a real violation
    assert len(after_index) == 1


# =========================================================================================
# (i) — the ownership tension is visible in the row, not argued about elsewhere
# =========================================================================================


def test_row_i_names_w37_10_as_its_owner(dv: Any, tmp_path: pathlib.Path) -> None:
    """Ruling 102 §1 requires nine rows; §3 rules (i) is W37-10's. Both hold at once only
    if the row is computed *and* its owner is printed."""
    snap = _snapshot(dv, tmp_path / "i", {"docs/a.md": "x\n"}, {"docs/a.md": "x\n"})
    row = dv.row_i(snap)
    assert row.key == "i"
    assert row.owner == dv.OWNER_W37_10
    assert "OWNERSHIP TENSION" in row.note


def test_row_i_verdict_is_disclose_not_fatal_when_h_rows_exist(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """Ruling 105 D1: `(i)` is W37-10's and does not set the exit code. Before this ruling
    the non-empty-population branch scored `NOT MEASURED` (fatal); it now scores `DISCLOSE`
    (non-fatal). Red-then-green against the row above: an empty population still fails
    (NT-0007), a real one now discloses rather than blocking the exit code."""
    body = "## 5. Impact\n| `x` | y | H |\n"
    tree = tmp_path / "t"
    (tree / "docs" / "notes").mkdir(parents=True)
    (tree / dv._NT0019_PATH).write_text(body, encoding="utf-8")
    snap = dv.Snapshot(
        workdir=tmp_path, ref="test", ref_sha="0" * 40,
        migrated=tree, control=tree, baseline=None, baseline_ref=None,
    )
    row = dv.row_i(snap)
    assert row.verdict == dv.DISCLOSE
    assert row.fatal is False
    assert row.owner == dv.OWNER_W37_10
    assert "Ruling 105 D1" in row.note


def test_h_row_predicate_counts_the_notes_section_5_tables(dv: Any) -> None:
    """Green: the shapes NT-0019 §5 actually uses. Red: a row whose kind column is not H."""
    assert dv._H_ROW_RE.match("| `README.md` | the tour: new paths | H |")
    assert dv._H_ROW_RE.match("| `a.py`, `b.py` | fixture ids | H + M |")
    assert not dv._H_ROW_RE.match("| `code suites` | comment rewrites only | M |")


def test_h_row_count_follows_the_migrations_own_redirect(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """The note moves to a slug derived from its *title*, so a filename guess finds
    nothing and the row would report an empty population as if it were an answer. It is
    followed through `docs/REDIRECTS.csv` instead — red before green: without the redirect
    row the count is 0; with it, 2."""
    body = (
        "## 5. Impact\n"
        "| `x` | y | H |\n"
        "| `z` | w | H + M |\n"
        "| `q` | r | M |\n"
        "## 6. Next\n"
        "| `s` | t | H |\n"
    )
    tree = tmp_path / "t"
    (tree / "docs" / "rfcs").mkdir(parents=True)
    (tree / "docs" / "rfcs" / "RFC-00216-one-id-per-governed-thing.md").write_text(
        body, encoding="utf-8"
    )
    assert dv._count_h_rows(tree) == 0
    (tree / "docs" / "REDIRECTS.csv").write_text(
        "old_id,new_id,old_path,new_path\n"
        f"NT-0019,RFC-216,{dv._NT0019_PATH},docs/rfcs/RFC-00216-one-id-per-governed-thing.md\n",
        encoding="utf-8",
    )
    assert dv._count_h_rows(tree) == 2  # §6's H row is not §5's


# =========================================================================================
# The whole instrument, end to end. Slow (a real archive plus a real migration), so it is
# opt-in locally and always on in CI, where it is the step Ruling 102 §1 wires in.
# =========================================================================================


@pytest.mark.skipif(
    not os.environ.get("DOC_ID_VERIFY_E2E"),
    reason="set DOC_ID_VERIFY_E2E=1 to run the full snapshot+migration (~4 minutes)",
)
def test_end_to_end_is_red_on_this_tree_and_names_its_rows(
    doc_id_cli: Any, tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Ruling 102 §1: *"It runs in CI ... and is red on `main` until green."*

    The assertion is deliberately on the *shape* of the answer, never on a figure: pinning
    a count here would make every corpus change a test failure and would tempt exactly the
    predicate-tuning the ruling forbids.
    """
    code = doc_id_cli.main(
        ["migrate", "--verify", str(tmp_path / "snap"), "--ref", "HEAD", "--no-baseline"]
    )
    out = capsys.readouterr().out
    assert code == 1
    for key in ("(a)", "(b)", "(c)", "(d1)", "(e)", "(f)", "(g)", "(h1)", "(i)"):
        assert key in out
    assert "predicate" in out
    assert "denominator" in out
    assert "control" in out


# =========================================================================================
# Companion predicates, REGRESSION and INERT — a row satisfiable by corruption
# =========================================================================================


def test_a_row_can_read_zero_because_corruption_moved_the_token_out_of_reach(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """Auditor finding A1, as a corpus. `F-W[0-9]` reads **0** on the migrated tree while
    the mangled form `F-WK-…` reads non-zero, and `F-WK` has a letter where the alternative
    wants a digit — so the row would be green *because* the corpus is damaged, were it not
    disclosed rather than scored.

    The row scores DISCLOSE (Ruling 105 §A — `F-W[0-9]` joins `\\bF[0-9]{2}\\b` as excluded
    from the zero requirement with its count disclosed, never PASS): promoting a companion
    to a gating row is still the maintainer's under Ruling 102 §1. What the instrument owes
    is that the evidence is **printed beside the number**, and that is what this asserts.
    """
    migrated = {"docs/a.md": "the finding F-WK-952-1-3 is cited here\n"}
    control = {"docs/a.md": "the finding F-W11-1-3 is cited here\n"}
    row = _d_rows(dv, _snapshot(dv, tmp_path / "a1", migrated, control))["d2"]
    assert row.verdict == dv.DISCLOSE
    assert row.fatal is False
    assert row.migrated.startswith("0 line")
    labels = {c[0]: c for c in row.companions}
    mangled = next(c for k, c in labels.items() if k.startswith("mangled"))
    assert mangled[1] == r"\bF-WK-[0-9]"
    assert "migrated 1 line(s)" in mangled[2]
    assert "control 0" in mangled[2]


def test_a_companion_is_promoted_to_gating_by_configuration_not_a_rewrite(
    dv: Any, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The lead's directive: built so a companion can be promoted by configuration.

    Red-then-green on the same corpus: the row discloses (Ruling 105 §A) with
    `GATING_COMPANIONS` empty and fails with one label named in it, and nothing else
    changes — `GATING_COMPANIONS` overrides even a disclosed verdict.
    """
    migrated = {"docs/a.md": "the finding F-WK-952-1-3 is cited here\n"}
    control = {"docs/a.md": "the finding F-W11-1-3 is cited here\n"}
    snap = _snapshot(dv, tmp_path / "promote", migrated, control)
    assert _d_rows(dv, snap)["d2"].verdict == dv.DISCLOSE
    label = "mangled: work key rewritten inside the finding id"
    monkeypatch.setattr(dv, "GATING_COMPANIONS", frozenset({label}))
    promoted = _d_rows(dv, snap)["d2"]
    assert promoted.verdict == dv.FAIL
    assert "GATING_COMPANIONS" in promoted.note


def test_an_alternative_with_no_companion_says_so_by_name(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """A silent absence would read as "asked and found nothing"."""
    snap = _snapshot(dv, tmp_path / "nocomp", _CLEAN, {"docs/a.md": "ADR-0004\n"})
    row = _d_rows(dv, snap)["d6"]  # ADR-0[0-9]{3}\b, no companion declared
    assert any(c[2].startswith("no companion predicate declared") for c in row.companions)


def test_d6_anchor_does_not_trip_on_a_correctly_migrated_five_digit_id(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """The peer executor's finding, folded into this ruling's follow-up (same file).

    `ADR-0[0-9]{3}` with no trailing anchor reads the first three of a five-digit padded
    id's four post-hyphen digits as a hit — `ADR-00999` (`_docid.PAD_WIDTH` = 5) contains
    `ADR-0099`. The trailing `\\b` this fix adds is the same device `\\bF[0-9]{2}\\b` already
    uses for its own boundary. Red-then-green on two distinct inputs: a genuinely
    un-migrated 4-digit legacy citation must still trip the row; a correctly-migrated
    5-digit citation must not.

    `ADR-999` rather than a real ADR, deliberately: highest allocated is `ADR-10`, and this
    file is inside the corpus row (e) scans, so a real number here would make this fixture a
    genuine `NT-0019` §7(e) violation — the same self-counting shape `RL-09999`/`PL-09998`
    above already guard against.
    """
    migrated_ok = {"docs/a.md": "see ADR-00999 for the decision\n"}
    row_ok = _d_rows(dv, _snapshot(dv, tmp_path / "d6ok", migrated_ok, _CLEAN))["d6"]
    assert row_ok.migrated.startswith("0 line"), (
        "a correctly-migrated five-digit id must not be read as a legacy citation"
    )

    migrated_bad = {"docs/a.md": "see ADR-0999 for the decision\n"}
    row_bad = _d_rows(dv, _snapshot(dv, tmp_path / "d6bad", migrated_bad, _CLEAN))["d6"]
    assert not row_bad.migrated.startswith("0 line"), (
        "a genuinely un-migrated 4-digit legacy citation must still trip the row"
    )


def test_fenced_legacy_form_excluded_from_row_d_but_an_unfenced_sibling_still_counts(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """W37-6 exec-ids specification-class disposition (Ruling 103 §5.1's fence clause,
    extended to row (d)'s corpus, 2026-09-04): an id-shaped exhibit kept byte-exact inside
    a fenced code block documents the FORM a legacy id takes, not a citation of a specific
    document, and must not count toward row (d)'s zero requirement — the identical reading
    row (e)'s own conjunct 0 already gives a padded id inside a fence.

    Two assertions, deliberately in one test, because the pair is the claim: the fenced
    occurrence is excluded, but an unfenced sibling on an adjacent line of the *same* file
    still counts — proving the exclusion is genuinely fence-scoped and not a document-keyed
    exemption (already refused for row (e), the same corpus, per the deputy's ruling).
    """
    migrated = {
        "docs/a.md": (
            "Illustrative examples the check was proven against:\n\n"
            "```\n"
            "NT-0042\n"
            "```\n\n"
            "and a genuine un-migrated citation on the next line: NT-0043\n"
        ),
    }
    d1 = _d_rows(dv, _snapshot(dv, tmp_path, migrated, _CLEAN))["d1"]
    assert d1.migrated.startswith("1 line"), (
        "the fenced NT-0042 must be excluded; only the unfenced NT-0043 counts"
    )


def test_d7_a_defined_token_left_unrewritten_still_fails(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """Broken-input proof, direction 1 (the deputy's mechanical predicate, 2026-09-04,
    W37-6 exec-ids, relayed via team-lead): a scoped id that IS bold-defined in the
    control tree's `docs/specs/` must never be excused into the never-allocated closed
    class merely because its citing line reads like an allocation marker — an
    unrewritten citation of a genuinely definable id is a real `token_map` miss and must
    FAIL, not disclose. Guards against the class swallowing real misses.
    """
    migrated = {
        "docs/specs/00-overview.md": "**FR-EX-1** A normal requirement.\n",
        "docs/plans/2026-01-01-x.md": "Next free: `FR-EX-1` — still cited, unrewritten.\n",
    }
    control = {
        "docs/specs/00-overview.md": "**FR-EX-1** A normal requirement.\n",
    }
    d7 = _d_rows(dv, _snapshot(dv, tmp_path, migrated, control))["d7"]
    assert d7.verdict == "FAIL", (
        f"a defined-but-unrewritten token must FAIL, not disclose: {d7.note}"
    )
    assert "FR-EX-1" in d7.note


def test_d7_an_undefined_token_is_disclosed_as_the_never_allocated_closed_class(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """Broken-input proof, direction 2: a scoped id with zero definition in every source
    `_discover_*` reads, and no `docs/REDIRECTS.csv` row, is the never-allocated closed
    class — disclosed, count and all, never failed and never rewritten.
    """
    text = "Next free: `FR-EX-999` — deliberately never taken.\n"
    migrated = {"docs/plans/2026-01-01-x.md": text}
    # Unrewritten means unchanged: the control side carries the identical value, so this
    # is not "creation" (a value present in migrated and absent from control) — the same
    # shape the real corpus has for a never-allocated token (nothing rewrites it, so
    # migrated and control agree byte-for-byte on that one citation).
    control = {"docs/plans/2026-01-01-x.md": text}
    d7 = _d_rows(dv, _snapshot(dv, tmp_path, migrated, control))["d7"]
    assert d7.verdict == "DISCLOSE", f"an undefined token must disclose: {d7.note}"
    assert "closed class" in d7.note
    assert "none — closed class" in d7.note


def test_unanchor_is_a_no_op_for_a_bare_path_literal_the_old_inert_case_is_fixed(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """The path entries carry no `\\b` at all under the shared constant (task 17) — a path
    has no "complete form" the way an id token does, so Ruling 67 §2 Part 1 anchors it as a
    bare literal substring, never `\\b`-wrapped. This is a genuine fix, not cosmetic: the
    OLD alternative (this row's own outer `\\b(...)` wrapper) needed a word character
    immediately before the dot to fire at all, so a backtick-quoted path with a dot right
    after the opening backtick — not a word character — never matched and the row read
    INERT (0 anchored, 88 unanchored) on real content. The new bare-literal form matches
    this exact input directly. (The path is not spelled anywhere in this file; see below.)"""
    # Built by concatenation for the reason `tests/test_notes_move_citations.py` builds its
    # own search term that way: this file is inside the corpus that test scans, and a
    # literal here would make it an offender.
    old_root = "." + "claude" + "/" + "notes"
    doc = f"see `{old_root}/README.md` and {old_root}/x.md\n"
    snap = _snapshot(dv, tmp_path / "inert", {"docs/a.md": doc}, {"docs/a.md": doc})
    row = _d_rows(dv, snap)["d13"]
    assert "legacy claude-notes path" in row.title
    assert row.migrated.startswith("1 line"), (
        "the bare-literal form must match this backtick-preceded occurrence directly, "
        "unlike the old outer-`\\b`-wrapped alternative"
    )
    unanchored = next(c for c in row.companions if c[0].startswith("unanchored"))
    # No `\b` to strip for a path literal: `_unanchor` is a no-op, so anchored and
    # unanchored read the identical figure — the INERT signature (control == migrated with
    # a nonzero unanchored gap) no longer applies to this alternative.
    assert "migrated 1" in unanchored[2]
    assert dv._unanchor(dict(dv.D_ALTERNATIVES)["legacy claude-notes path"].pattern) == (
        dict(dv.D_ALTERNATIVES)["legacy claude-notes path"].pattern
    )


def test_an_alternative_that_gets_worse_is_a_regression_not_a_fail(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """(d4) `wf-0[0-9]`, 267 -> 327. The migration CREATES what the row forbids, so no
    citation rewrite reaches zero. That is not a bigger version of "did not reach zero" —
    and, per the 2026-09-04 ruling (`to-lead.md:1017`), it is specifically a *new value*
    (`wf-02`, absent from control), not merely a larger occurrence count."""
    migrated = {"docs/a.md": "wf-01 here\n", "docs/b.md": "wf-02 there\n"}
    control = {"docs/a.md": "wf-01 here\n", "docs/b.md": "nothing\n"}
    row = _d_rows(dv, _snapshot(dv, tmp_path / "reg", migrated, control))["d4"]
    assert row.verdict == dv.REGRESSION
    assert row.fatal
    assert "wf-02" in row.note


def test_an_alternative_with_a_larger_occurrence_count_but_the_same_values_is_not_a_regression(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """The 2026-09-04 ruling itself (`to-lead.md:1017`), stated from the measurement that
    provoked it: `W37-6` 685->725 and `W32-7` 68->78 on the real corpus, value set
    identical both times — not creation, a disclosure line. Reproduced narrowly: `wf-01`
    cited twice in the migrated tree, once in control, with no other value anywhere.
    (d4) must not regress on the count alone."""
    migrated = {"docs/a.md": "wf-01 here\n", "docs/b.md": "wf-01 there too\n"}
    control = {"docs/a.md": "wf-01 here\n", "docs/b.md": "nothing\n"}
    row = _d_rows(dv, _snapshot(dv, tmp_path / "growth", migrated, control))["d4"]
    assert row.verdict != dv.REGRESSION
    assert "wf-01 1->2" in row.note, row.note


# =========================================================================================
# (d8) — Ruling 105 §A's third alias class: slice keys AND task keys disclosed (task keys
# joined by Ruling #26, `to-lead.md:498-510`, reaffirmed at `to-lead.md:1298-1306`), only
# the bare work-key remainder stays fatal, creation stays REGRESSION despite the disclosure
# =========================================================================================


def test_d8_slice_key_alone_is_disclosed(dv: Any, tmp_path: pathlib.Path) -> None:
    """A plain two-segment slice key, no task key and no bare work-key remainder in
    sight: the whole row discloses rather than fails."""
    migrated = {"docs/a.md": "see W11-1 for the plan\n"}
    control = {"docs/a.md": "see W11-1 for the plan\n"}
    row = _d_rows(dv, _snapshot(dv, tmp_path / "d8slice", migrated, control))["d8"]
    assert row.verdict == dv.DISCLOSE
    assert row.fatal is False
    assert "slice-key and task-key population disclosed" in row.note
    assert "owner W37-11" in row.note


def test_d8_task_key_is_disclosed_alongside_the_slice_key(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """A three-segment task key on the same row as a clean slice key: it joins the
    DISCLOSED component and is counted on its own line, rather than failing the row.

    Ruling #26 (`to-lead.md:498-510`), reaffirmed against the decision-maker's own two
    later entries by the correction at `to-lead.md:1298-1306`: *"no family exists for a
    task (NT-0019 §1.2 has `WK` and `SL`, nothing below a slice), so a task key has no
    target by the standard's design — the same ground as slice keys."* That correction
    also states the fatal set positively — *"The fatal component of d8 is therefore the
    bare work-key remainder only ... plus creation"* — and its violation line reads
    *"task keys treated as fatal anywhere after this"*.

    This test previously asserted the opposite (`..._task_key_stays_fatal_...`), written
    against the superseded 19:xxZ instruction; the counts, not just the verdict, are
    asserted here so the disclosure cannot silently degrade into an unreported skip."""
    migrated = {"docs/a.md": "see W11-1 and also W11-1-2\n"}
    control = {"docs/a.md": "see W11-1 and also W11-1-2\n"}
    row = _d_rows(dv, _snapshot(dv, tmp_path / "d8task", migrated, control))["d8"]
    assert row.verdict == dv.DISCLOSE
    assert row.fatal is False
    assert "slice-key and task-key population disclosed" in row.note
    assert "task-key 1 line(s) / 1 file(s)" in row.note
    assert "slice-key 1 line(s) / 1 file(s)" in row.note


def test_d8_bare_work_key_remainder_stays_fatal(dv: Any, tmp_path: pathlib.Path) -> None:
    """A bare `W<n>` with no slice number at all is a `token_map` defect, not the alias
    class — it must fail the row even with no task key present."""
    migrated = {"docs/a.md": "see W11-1 and the bare W12 citation\n"}
    control = {"docs/a.md": "see W11-1 and the bare W12 citation\n"}
    row = _d_rows(dv, _snapshot(dv, tmp_path / "d8bare", migrated, control))["d8"]
    assert row.verdict == dv.FAIL
    assert row.fatal
    assert "bare work-key remainder(s)" in row.note
    assert "token_map defect" in row.note


def test_d8_creation_stays_regression_even_though_the_class_is_disclosed(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """Ruling 105 §A: "creation... stays REGRESSION even for a disclosed class, because a
    disclosed count that grows is the mangling class, not the alias class." A slice key
    the migration CREATES (migrated > control on the whole alternative) must not just
    disclose quietly — it must still fail as REGRESSION, checked before the disclosure."""
    migrated = {"docs/a.md": "W11-1 here\n", "docs/b.md": "W11-2 there\n"}
    control = {"docs/a.md": "W11-1 here\n", "docs/b.md": "nothing\n"}
    row = _d_rows(dv, _snapshot(dv, tmp_path / "d8creation", migrated, control))["d8"]
    assert row.verdict == dv.REGRESSION
    assert row.fatal
    assert "creation stays REGRESSION" in row.note


def test_d8_slice_key_regex_does_not_double_count_a_task_key_as_a_slice_key(
    dv: Any,
) -> None:
    """The negative lookahead's whole job: `W11-1` must not also register as a slice key
    when it is really the first two segments of `W11-1-2`."""
    assert dv._D8_SLICE_KEY_RE.search("see W11-1-2 here") is None
    assert dv._D8_SLICE_KEY_RE.search("see W11-1 here")
    assert dv._D8_TASK_KEY_RE.search("see W11-1-2 here")
    assert dv._D8_WORK_KEY_BARE_RE.search("see W11-1 here") is None
    assert dv._D8_WORK_KEY_BARE_RE.search("see W11 alone here")


def test_an_alternative_the_migration_does_not_move_is_marked_inert(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """The auditor's two-column signature: control == migrated means no discriminating
    power, whatever the absolute figure looks like."""
    same = {"docs/a.md": "NT-0019 is cited\n"}
    row = _d_rows(dv, _snapshot(dv, tmp_path / "inert2", same, same))["d1"]
    assert "INERT" in row.note


# =========================================================================================
# Row (c) — the string, not the exit code
# =========================================================================================


def test_row_c_asserts_the_byte_stable_string_because_three_states_share_exit_0(
    dv: Any,
) -> None:
    """Measured by the auditor: exit 0 is returned by a genuine pass, by an un-migrated
    tree, and by a fully migrated tree checked with `--root` off by one directory — the
    last of which prints the reassuring pre-migration line over an untouched corpus."""
    assert dv._BYTE_STABLE == "OK (byte-stable)"
    assert dv._NOTHING_TO_CHECK == "nothing to check yet"


def test_run_script_refuses_a_script_outside_the_snapshot(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """The tree's-own-copy rule, enforced rather than commented. Using the checkout's
    `doc-index.py` turns row (c) from a fail into a pass, which would make the defect
    invisible to the instrument built to detect it."""
    tree = tmp_path / "snap"
    (tree / "scripts").mkdir(parents=True)
    with pytest.raises(dv.WorkingCheckoutRefusedError):
        dv._run_script(tree, "../../../etc/doc-index.py")


# =========================================================================================
# (h) — non-executing checks, and the over-exemption shape
# =========================================================================================


def test_a_check_that_cannot_run_is_counted_separately_from_one_that_failed(
    dv: Any,
) -> None:
    """Non-execution is a third state beside pass and fail, and a failure count scores it
    as a small number of failures rather than as a hole in coverage."""
    out = (
        "  docs/notes does not exist — checks 16-20 cannot run\n"
        "  docs/notes does not exist — check 25 cannot scan it\n"
        "  check 3: fine\n"
    )
    assert len(dv._ABSENT_CHECK_RE.findall(out)) == 2
    assert len(dv._ABSENT_CHECK_RE.findall("  check 3: fine\n")) == 0


# =========================================================================================
# (h1) — the per-class breakdown, Ruling 105 §B
# =========================================================================================


_FAILED_BLOCK = (
    "  check 29: register grammar — 0 violation(s)\n"
    "\n"
    "FAILED (5):\n"
    "  - check 32: docs/a.md: PL-09998 does not resolve in docs/INDEX.md\n"
    "  - check 32: docs/b.md: PL-09999 does not resolve in docs/INDEX.md\n"
    "  - check 29: docs/audit/register.md: bad Decision cell\n"
    "  - check 30: docs/c.md: no front-matter header\n"
    "  - check 1: broken link in docs/d.md: docs/gone.md\n"
)


def test_classify_failures_reads_only_the_failed_block_by_check_number(dv: Any) -> None:
    """Ruling 105 §B's own methodology (`docs/plans/…row-h-the-named-h-rows.md:139`), ported
    to Python: a note line mentioning `check 29:` before `FAILED (`n`):` must not be counted
    — only the `  - ` failure lines after it. `broken link in …` (check 1's own message
    shape) classifies by its own `check 1:` prefix like every other check, since
    `scripts/audit-docs.py` now writes it — no special case for this shape any more (the
    deputy's ruling on exec-h1's classifier-gap finding: fix every check's message at the
    source, never grow a per-check special case in this predicate)."""
    classes = dv._classify_failures(_FAILED_BLOCK)
    assert classes == {"32": 2, "29": 1, "30": 1, "1": 1}
    assert sum(classes.values()) == 5  # not 6 — the pre-FAILED note line is excluded


def test_classify_failures_counts_an_unattributable_message_rather_than_dropping_it(
    dv: Any,
) -> None:
    """§13 admits no silence: a failure message this predicate cannot map to a check number
    is still counted, under `"unclassified"`, never dropped from the total."""
    out = "FAILED (1):\n  - docs/a.md: header block is missing the **Sequencing** field\n"
    classes = dv._classify_failures(out)
    assert classes == {"unclassified": 1}


def test_classify_failures_is_empty_when_the_tree_is_clean(dv: Any) -> None:
    assert dv._classify_failures("All checks passed.\n") == {}


def test_h1_verdict_passes_only_when_every_other_class_is_zero(dv: Any) -> None:
    """Ruling 105 §B: checks 29/30/35 are excluded from the zero requirement, but every
    other class — 32, 36, 1, 31, 27, and anything not named — must be zero to pass."""
    assert dv._h1_verdict(0) == dv.PASS
    assert dv._h1_verdict(1) == dv.FAIL


def test_h2_verdict_over_exempt_discloses_but_vacuous_stays_fatal(dv: Any) -> None:
    """Ruling 105 D3: the zero-denominator probes (`vacuous`) stay fatal even when
    OVER-EXEMPT also fires; OVER-EXEMPT alone is disclosed, not failed."""
    assert dv._h2_verdict([], False) == dv.PASS
    assert dv._h2_verdict([], True) == dv.DISCLOSE
    assert dv._h2_verdict(["requirements defined"], False) == dv.FAIL
    assert dv._h2_verdict(["requirements defined"], True) == dv.FAIL


def test_over_exemption_is_a_vacuity_the_zero_denominator_rule_cannot_see(
    dv: Any,
) -> None:
    """The auditor's post-H-rows hazard: check 37 exempting ~353 of ~424 documents on a
    `was:` field that is right 3 times in ~393. A large population almost entirely
    excused, not an empty one — the denominators are all non-zero."""
    assert dv._EXEMPTION_FLOOR == 20
    assert dv._EXEMPTION_RATE_CAP == 0.5
    over = dv._probe_summary(
        "  check 37: 424 document(s) checked in scope, 353 exempt as verbatim-migrated\n"
    )
    assert over["check 37 documents in scope"] == 424
    assert over["check 37 `was:` exemptions"] == 353
    # Non-zero denominators throughout: the zero-denominator rule is silent here.
    assert over["check 37 documents in scope"] != 0
    # The pre-H-row state must NOT trip it — 0 of 1 is not evidence of anything.
    pre = dv._probe_summary(
        "  check 37: 1 document(s) checked in scope, 0 exempt as verbatim-migrated\n"
    )
    assert (pre["check 37 documents in scope"] or 0) < dv._EXEMPTION_FLOOR


# =========================================================================================
# The recorded verdict set — a new failure distinguishable from the standing red (F102)
# =========================================================================================


def _row(dv: Any, key: str, verdict: str) -> Any:
    return dv.Row(
        key=key, title="t", owner="W37-6", predicate="p", denominator="d",
        migrated="m", control="c", verdict=verdict,
    )


def _result(dv: Any, verdicts: dict[str, str]) -> Any:
    snap = dv.Snapshot(
        workdir=pathlib.Path("/nonexistent"), ref="t", ref_sha="0" * 40,
        migrated=pathlib.Path("/nonexistent"), control=pathlib.Path("/nonexistent"),
        baseline=None, baseline_ref=None,
    )
    return dv.VerifyResult(
        snapshot=snap, rows=tuple(_row(dv, k, v) for k, v in verdicts.items())
    )


def test_the_standing_red_is_not_a_set_change(dv: Any) -> None:
    """The base case that makes the signal worth anything: every run until the migration
    lands is red, and a red that moved nothing must say so."""
    result = _result(dv, dict(dv.EXPECTED_VERDICTS))
    assert result.set_changes == ()
    assert result.exit_code == 1
    assert "UNCHANGED" in dv.render(result)


def test_f102s_own_regression_is_detected_without_a_baseline(dv: Any) -> None:
    """F102, as its broken-input proof. An audit record added under `docs/audit/` with an
    ordinary descriptive name took row (a) from `none=0` to `none=1` — **the only passing
    row** — while `audit-docs.py`, `register-lint.py` and the whole local gate stayed green.
    Exit 1 was true before it and after it."""
    moved = dict(dv.EXPECTED_VERDICTS, a=dv.FAIL)
    result = _result(dv, moved)
    changes = result.set_changes
    assert [(c.key, c.direction) for c in changes] == [("a", dv.REGRESSED)]
    assert result.exit_code == 3, "a moved row must not share exit 1 with the standing red"
    out = dv.render(result)
    assert "SET CHANGE" in out
    assert "REGRESSION (newly failing): (a) PASS -> FAIL" in out


def test_progress_is_a_set_change_too_and_says_what_to_edit(dv: Any) -> None:
    """Deliberately, and this is the half that stops the baseline going stale. A row fixed
    and left in the table would mask its own later regression, so progress is reported —
    with the edit it requires — rather than passed over.

    "d9" rather than "b"/"c"/"e": every one of those three has since moved off FAIL at
    some point in this row's own history and would make the `dict(..., key=PASS)`
    override a no-op against the real recorded table — exactly the false-pass this test
    exists to guard against elsewhere. "b" flips between FAIL and PASS across #707/#708's
    re-recording and #711's regression (task 17, 2026-09-04); "c" and "e" are both PASS as
    of this commit ("e" folded in here — angle-bracket boundary and same-line duplicate-
    token fixes). "d9" (a literal legacy-path alternative in (d), not yet migrated) has no
    such history and stays FAIL.
    """
    assert dv.EXPECTED_VERDICTS["d9"] == dv.FAIL, (
        "this test's premise: the row it moves must start FAIL in the real table"
    )
    moved = dict(dv.EXPECTED_VERDICTS, d9=dv.PASS)
    result = _result(dv, moved)
    assert [(c.key, c.direction) for c in result.set_changes] == [("d9", dv.PROGRESSED)]
    assert result.exit_code == 3
    out = dv.render(result)
    assert "PROGRESS (newly passing): (d9) FAIL -> PASS" in out
    assert "same commit as the change that moved the row" in out


def test_a_reclassification_between_two_fatal_verdicts_is_a_set_change(dv: Any) -> None:
    """(d4) going FAIL -> REGRESSION is a finding, not noise: the migration began creating
    what the row forbids. A fatal-to-fatal move must not be invisible.

    "d9" rather than "d1" or "d5": task 17 (2026-09-04) re-recorded (d5) as PASS on
    `main` (#711's unrelated progress), and W37-6 exec-ids (2026-09-04) fixed (d1) to
    PASS in the same table, so a FAIL -> REGRESSION override at either would actually be
    a PASS -> REGRESSION move (REGRESSED, not RECLASSIFIED) against the real table. "d9"
    (legacy dated-plan path) stays FAIL — a genuine fatal-to-fatal example, owned by
    W37-6's path-repointing track, untouched by this row's own fix.
    """
    assert dv.EXPECTED_VERDICTS["d9"] == dv.FAIL, (
        "this test's premise: the row it moves must start FAIL (fatal) in the real table"
    )
    moved = dict(dv.EXPECTED_VERDICTS, d9=dv.REGRESSION)
    result = _result(dv, moved)
    assert [(c.key, c.direction) for c in result.set_changes] == [("d9", dv.RECLASSIFIED)]
    assert result.exit_code == 3


def test_a_row_added_or_dropped_is_a_set_change(dv: Any) -> None:
    """A row added without a table entry, or a row that silently stopped being computed.
    The second is the more dangerous: a dropped row reduces the failure count, which reads
    like progress."""
    added = _result(dv, dict(dv.EXPECTED_VERDICTS, z9=dv.FAIL))
    assert [(c.key, c.direction) for c in added.set_changes] == [("z9", dv.ROW_ADDED)]
    dropped_verdicts = dict(dv.EXPECTED_VERDICTS)
    del dropped_verdicts["g"]
    dropped = _result(dv, dropped_verdicts)
    assert [(c.key, c.direction) for c in dropped.set_changes] == [("g", dv.ROW_REMOVED)]
    assert dropped.exit_code == 3


def test_all_green_exits_zero_and_is_not_a_set_change_once_recorded(dv: Any) -> None:
    """The end state. When every row is green AND the table says so, the instrument exits
    0 — the condition Ruling 102 §1's go-ahead is defined as."""
    green = {k: dv.PASS for k in dv.EXPECTED_VERDICTS}
    monkey = dv.EXPECTED_VERDICTS
    try:
        dv.EXPECTED_VERDICTS = green
        assert _result(dv, green).exit_code == 0
    finally:
        dv.EXPECTED_VERDICTS = monkey


def test_the_recorded_set_covers_every_row_the_instrument_computes(dv: Any) -> None:
    """A structural guard on the table itself: every key it records must be a key some row
    function produces, and the row keys are stable by construction."""
    expected_keys = set(dv.EXPECTED_VERDICTS)
    known = {"a", "b", "c", "e", "f", "g", "h1", "h2", "h3", "h4", "i"} | {
        f"d{i}" for i in range(1, len(dv.D_ALTERNATIVES) + 1)
    }
    assert expected_keys == known


def test_the_set_change_block_is_printed_at_both_ends(dv: Any) -> None:
    """A CI log is read from the end and a long table is skimmed from the top; a reader
    should not have to reach either."""
    out = dv.render(_result(dv, dict(dv.EXPECTED_VERDICTS, a=dv.FAIL))).splitlines()
    heads = [i for i, line in enumerate(out) if line.startswith("SET CHANGE")]
    assert len(heads) == 2
    assert heads[0] < len(out) // 2 < heads[1]
