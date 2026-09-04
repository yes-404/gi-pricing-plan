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
from typing import Any

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
    assert "empty population" in rows["d1"].note


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
    """`\\bF[0-9]{2}\\b` is excluded from the zero requirement **with its count disclosed**."""
    migrated = {"docs/a.md": "F41 and F85 and F96\n"}
    control = {"docs/a.md": "F41\n"}
    snap = _snapshot(dv, tmp_path / "disc", migrated, control)
    rows = _d_rows(dv, snap)
    assert rows["d3"].verdict == dv.DISCLOSE
    assert rows["d3"].fatal is False
    assert rows["d3"].migrated.startswith("1 line")  # one *line*, three occurrences


def test_every_d_alternative_is_a_branch_of_the_full_pattern(dv: Any) -> None:
    """The decomposition cannot drift from §7(d)'s own sentence.

    Every alternative must appear verbatim inside `D_FULL_PATTERN`, and there must be one
    row per leaf — thirteen, matching the handover's per-alternative table.
    """
    for alt in dv.D_ALTERNATIVES:
        if alt.startswith("docs/"):
            continue  # the four leaves of `docs/(plans/2026-|audit/|notes/|adr/)`
        assert alt in dv.D_FULL_PATTERN, alt
    assert len(dv.D_ALTERNATIVES) == 13


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


# =========================================================================================
# Task 17 — the decomposition is derived from the acceptance sentence, not retyped
# =========================================================================================


def test_the_alternatives_are_derived_and_reproduce_the_hand_written_list(
    dv: Any,
) -> None:
    """The list this replaced was hand-typed, and one of its entries was the very string
    row (d11) forbids — so the instrument counted its own source. Derivation removes the
    literal; this pins that it removed nothing else."""
    expected = (
        "NT-00", "F-W[0-9]", r"\bF[0-9]{2}\b", "wf-0[0-9]", "Ruling [0-9]+",
        # trailing `\b` added, disclosed deviation from the spec sentence's literal text —
        # the token-boundary fix folded into this ruling's follow-up (same file, peer
        # executor's finding): without it the alternative matches as a prefix of any
        # correctly-migrated five-digit id.
        r"ADR-0[0-9]{3}\b", "(FR|NFR|OQ|DEP)-[A-Z]+-[0-9]+", "W[0-9]+[a-z]?-[0-9]+",
        # built by concatenation: this file is inside the corpus row (d) scans
        "docs/" + "plans/2026-", "docs/" + "audit/", "docs/" + "notes/", "docs/" + "adr/",
        r"\." + "claude/notes/",
    )
    assert expected == dv.D_ALTERNATIVES


def test_only_a_trailing_group_is_distributed(dv: Any) -> None:
    """The rule that makes the decomposition derivable rather than a matter of taste. A
    suffix group's leaves are separate things to count; a prefix group is one shape."""
    assert dv._expand_trailing_alternation("docs/(a/|b/)") == ["docs/a/", "docs/b/"]
    assert dv._expand_trailing_alternation("(FR|NFR)-[A-Z]+-[0-9]+") == [
        "(FR|NFR)-[A-Z]+-[0-9]+"
    ]


def test_the_splitter_respects_groups_classes_and_escapes(dv: Any) -> None:
    assert dv._split_top_level("a|b") == ["a", "b"]
    assert dv._split_top_level("(a|b)|c") == ["(a|b)", "c"]
    assert dv._split_top_level(r"[a|b]|c") == [r"[a|b]", "c"]
    assert dv._split_top_level(r"a\|b|c") == [r"a\|b", "c"]


@pytest.mark.parametrize("broken", ["a|(b", "a|b)", "a|[bc"])
def test_a_splitting_bug_raises_rather_than_returning_a_wrong_list(
    dv: Any, broken: str
) -> None:
    """The honest objection to deriving is that a splitting bug would be a **silent** wrong
    predicate, which is worse than the one-line floor it removes. It cannot be silent."""
    with pytest.raises(dv.PatternDecompositionError):
        dv._split_top_level(broken)


def test_the_derived_set_is_checked_against_its_source_over_the_real_corpus(
    dv: Any, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The runtime guard, red-then-green. Every line the acceptance sentence matches must be
    matched by some derived alternative and vice versa; drop one and it raises."""
    doc = {"docs/a.md": "cites ADR-0004 and NT-0019\n"}
    corpus = dv.load_corpus(_snapshot(dv, tmp_path / "dec", doc, doc).migrated)
    assert dv.assert_decomposition_matches_source(corpus) == 1
    monkeypatch.setattr(
        dv, "D_ALTERNATIVES", tuple(a for a in dv.D_ALTERNATIVES if a != r"ADR-0[0-9]{3}\b")
    )
    doc2 = {"docs/a.md": "cites ADR-0004 only\n"}
    corpus2 = dv.load_corpus(_snapshot(dv, tmp_path / "dec2", doc2, doc2).migrated)
    with pytest.raises(dv.PatternDecompositionError):
        dv.assert_decomposition_matches_source(corpus2)


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
    id's four post-hyphen digits as a hit — `ADR-00004` (`_docid.PAD_WIDTH` = 5) contains
    `ADR-0000`. The trailing `\\b` this fix adds is the same device `\\bF[0-9]{2}\\b` already
    uses for its own boundary. Red-then-green on two distinct inputs: a genuinely
    un-migrated 4-digit legacy citation must still trip the row; a correctly-migrated
    5-digit citation must not.
    """
    migrated_ok = {"docs/a.md": "see ADR-00004 for the decision\n"}
    row_ok = _d_rows(dv, _snapshot(dv, tmp_path / "d6ok", migrated_ok, _CLEAN))["d6"]
    assert row_ok.migrated.startswith("0 line"), (
        "a correctly-migrated five-digit id must not be read as a legacy citation"
    )

    migrated_bad = {"docs/a.md": "see ADR-0004 for the decision\n"}
    row_bad = _d_rows(dv, _snapshot(dv, tmp_path / "d6bad", migrated_bad, _CLEAN))["d6"]
    assert not row_bad.migrated.startswith("0 line"), (
        "a genuinely un-migrated 4-digit legacy citation must still trip the row"
    )


def test_the_unanchored_companion_distinguishes_an_inert_predicate(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """§7(d)'s thirteenth alternative is inert: its leading `\\b` needs a word character
    before the dot, so it cannot fire in any context it exists to police. Anchored 0,
    unanchored 2 — a genuinely clean alternative reads 0 against 0, and the pair is what
    tells them apart. (The path is not spelled anywhere in this file; see below.)"""
    # Built by concatenation for the reason `tests/test_notes_move_citations.py` builds its
    # own search term that way: this file is inside the corpus that test scans, and a
    # literal here would make it an offender. `scripts/_docverify.py` gets a reviewed
    # exemption instead, because there the literal IS the artifact — `D_FULL_PATTERN` is
    # §7(d)'s grep verbatim and hiding a branch of it would defeat the constant's purpose.
    # A test fixture has no such claim, so it takes the cheap route.
    old_root = "." + "claude" + "/" + "notes"
    doc = f"see `{old_root}/README.md` and {old_root}/x.md\n"
    snap = _snapshot(dv, tmp_path / "inert", {"docs/a.md": doc}, {"docs/a.md": doc})
    row = _d_rows(dv, snap)["d13"]
    anchored = re.compile(r"\b(" + dv.D_ALTERNATIVES[12] + ")")
    assert not anchored.search(doc), "the anchored alternative cannot match either occurrence"
    unanchored = next(c for c in row.companions if c[0].startswith("unanchored"))
    assert "migrated 1" in unanchored[2]  # one *line* carries both occurrences


def test_an_alternative_that_gets_worse_is_a_regression_not_a_fail(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """(d4) `wf-0[0-9]`, 267 -> 327. The migration CREATES what the row forbids, so no
    citation rewrite reaches zero. That is not a bigger version of "did not reach zero"."""
    migrated = {"docs/a.md": "wf-01 here\n", "docs/b.md": "wf-02 there\n"}
    control = {"docs/a.md": "wf-01 here\n", "docs/b.md": "nothing\n"}
    row = _d_rows(dv, _snapshot(dv, tmp_path / "reg", migrated, control))["d4"]
    assert row.verdict == dv.REGRESSION
    assert row.fatal
    assert "1 -> 2" in row.note


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
    "  - broken link in docs/d.md: docs/gone.md\n"
)


def test_classify_failures_reads_only_the_failed_block_by_check_number(dv: Any) -> None:
    """Ruling 105 §B's own methodology (`docs/plans/…row-h-the-named-h-rows.md:139`), ported
    to Python: a note line mentioning `check 29:` before `FAILED (`n`):` must not be counted
    — only the `  - ` failure lines after it — and `broken link in …` classifies as check 1,
    the one shape with no `check N:` prefix."""
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
    with the edit it requires — rather than passed over."""
    moved = dict(dv.EXPECTED_VERDICTS, b=dv.PASS)
    result = _result(dv, moved)
    assert [(c.key, c.direction) for c in result.set_changes] == [("b", dv.PROGRESSED)]
    assert result.exit_code == 3
    out = dv.render(result)
    assert "PROGRESS (newly passing): (b) FAIL -> PASS" in out
    assert "same commit as the change that moved the row" in out


def test_a_reclassification_between_two_fatal_verdicts_is_a_set_change(dv: Any) -> None:
    """(d4) going FAIL -> REGRESSION is a finding, not noise: the migration began creating
    what the row forbids. A fatal-to-fatal move must not be invisible."""
    moved = dict(dv.EXPECTED_VERDICTS, d5=dv.REGRESSION)
    result = _result(dv, moved)
    assert [(c.key, c.direction) for c in result.set_changes] == [("d5", dv.RECLASSIFIED)]
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
