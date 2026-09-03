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


def test_row_e_is_undetermined_and_prints_both_readings(
    dv: Any, tmp_path: pathlib.Path
) -> None:
    """Ruling 102 §2 row 5. A row with two readings is red, and *both* numbers are on the
    table — the instrument does not pick the more convenient one."""
    migrated = {"docs/a.md": "see PL-01240 and docs/plans/PL-01240-slug.md\n"}
    snap = _snapshot(dv, tmp_path / "e", migrated, migrated)
    row = dv.row_e(dv.load_corpus(snap.migrated), dv.load_corpus(snap.control))
    assert row.verdict == dv.UNDETERMINED
    assert row.fatal
    assert "reading 1 = 2" in row.migrated  # both occurrences
    assert "reading 2 = 1" in row.migrated  # only the one outside path context


def test_padded_id_in_path_context_is_distinguished_from_prose(
    dv: Any,
) -> None:
    """The path-context rule on the markdown-link form.

    `[PL-01240-slug](docs/plans/PL-01240-slug.md)` carries the id twice. The **target** is
    unambiguously a path and is excluded. The **link text** is a bare slug with no `/` and
    no extension, so the enclosing-token rule counts it — the larger, conservative reading.
    That residual judgement is exactly why row (e) is `UNDETERMINED` rather than scored:
    Ruling 102 §2 row 5 gives the choice to the decision-maker, and an instrument that
    quietly picked the smaller number would be making it.
    """
    line = "[PL-01240-slug](docs/plans/PL-01240-slug.md) and bare PL-01240 in a sentence"
    hits = list(dv._PADDED_ID_RE.finditer(line))
    assert len(hits) == 3
    prose = [h for h in hits if not dv._in_path_context(line, h.start(), h.end())]
    # the link *target* is path context; the link text and the bare id are not
    assert len(prose) == 2
    assert line[prose[-1].start():prose[-1].end()] == "PL-01240"


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
