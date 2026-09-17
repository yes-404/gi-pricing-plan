"""Git history is a **declared input** to id allocation — the proofs for W37-6 PR-A.

`docs/notes/0019-one-id-per-document.md` item 1 keys a requirement's `created` on "the
module's first-commit date; git first-commit date otherwise", and D1 at `:247` holds that
numbers carry chronology. `created` is `_sort_key`'s primary component and `_assign_numbers`
consumes that order, so git history is not context the migration happens to run in: it is
an input the allocation is a function of.

Three things are proven here, and the third is the one that matters.

1. **The refusal fires, by name, on deliberately broken input** — a plain directory and a
   shallow clone. Two different failures: a plain directory yields *no* date, while a
   shallow clone yields the shallow boundary commit, a well-formed *wrong* date that
   nothing downstream could distinguish from the right one. A check that has never printed
   its failure has not been tested (`CLAUDE.md` §13).

2. **`git archive` + `git init` allocates differently, and the instrument no longer builds
   one.** That was `_docverify._materialise`'s old construction: content-correct,
   history-less. Note the mechanism, because it is *not* the one this work was briefed
   with: such a snapshot does not hit any fallback. `git init` + `git commit` gives every
   file a valid adding commit, so the first-commit date reads back as the **synthetic
   commit's** date — well-formed, identical for every draft, and wrong. The sort then
   collapses onto its `(source path, index)` tie-break and stops being a function of
   chronology at all, which is why `--verify` measured an allocation no real run would
   produce while no row said so. No refusal can catch that shape; the fix is that the
   snapshot is a clone now.

3. **Two materialisations of one ref allocate identically, on different days.** This is the
   acceptance test, and it has a trap in it. The migration used to stamp `created:
   date.today()` into generated headers, which makes two runs *on the same day*
   byte-identical **even with the defect fully present** — today's reproduction of the real
   run held by luck of the calendar. So the clock is varied here, twice and in two
   different ways: once shifted to a date years away (the output must not move), and once
   made to raise on any read at all (the migration must complete). A test that cannot fail
   is worse than no test, and equality under an unvaried clock is exactly that.

No `@pytest.mark.req` marker, for the reason `tests/test_doc_id_migrate.py`'s module
docstring gives: this is correctness of a tool, not evidence for a numbered requirement.
"""

from __future__ import annotations

import datetime
import importlib.util
import pathlib
import shutil
import subprocess
import sys
from typing import Any

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOC_ID_SCRIPT_PATH = ROOT / "scripts" / "doc-id.py"
FIXTURE_CORPUS = ROOT / "tests" / "fixtures" / "docs-migration"

if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))


def _load(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, DOC_ID_SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_docverify() -> Any:
    """`scripts/_docverify.py` by path, the idiom every other test module here uses — it is
    a sibling script, not an importable package, so `mypy` cannot see it either."""
    spec = importlib.util.spec_from_file_location(
        "_docverify_history_input", ROOT / "scripts" / "_docverify.py"
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def doc_id_cli() -> Any:
    return _load("_doc_id_history_input_under_test")


@pytest.fixture(autouse=True)
def _no_declared_fixture_date(
    doc_id_cli: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Every test here is about what happens when history is *absent and undeclared*.

    `tests/test_doc_id_migrate.py` declares `DOCID_FIXTURE_CREATED_DATE` for its whole
    module — its corpora are directories by design. This module must run with that
    declaration off, or the refusals it exists to prove would be satisfied by it instead.
    """
    monkeypatch.delenv("DOCID_FIXTURE_CREATED_DATE", raising=False)
    monkeypatch.setattr(doc_id_cli, "_FIXTURE_CREATED_DATE", None)
    doc_id_cli._root_is_shallow.cache_clear()


def _git(args: list[str], cwd: pathlib.Path, env: dict[str, str] | None = None) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=True, env=env
    )
    return proc.stdout


def _multi_day_repo(dest: pathlib.Path) -> pathlib.Path:
    """The fixture corpus committed one spec at a time, on distinct days, in reverse order.

    Distinct dates, not one seed commit: the whole point is that `created` differs between
    modules and therefore *orders* them. A single-commit corpus would make every
    first-commit date identical, which is the very degeneracy the archive-and-init snapshot
    produced — a test built on it could not tell a correct allocation from a collapsed one.
    """
    shutil.copytree(FIXTURE_CORPUS, dest)
    _git(["init", "--initial-branch=main", "--quiet"], cwd=dest)
    _git(["config", "user.email", "t@t"], cwd=dest)
    _git(["config", "user.name", "Test"], cwd=dest)
    specs = sorted((dest / "docs" / "specs").glob("*.md")) if (
        dest / "docs" / "specs"
    ).is_dir() else []
    # Everything except the specs first, then one spec per day, so the specs' first-commit
    # dates are genuinely spread and genuinely ordered.
    import os

    def _commit(paths: list[str], day: int, message: str) -> None:
        stamp = f"2020-01-{day:02d}T12:00:00+00:00"
        env = {
            **os.environ,
            "GIT_AUTHOR_DATE": stamp,
            "GIT_COMMITTER_DATE": stamp,
        }
        for rel in paths:
            _git(["add", "--", rel], cwd=dest)
        _git(["-c", "commit.gpgsign=false", "commit", "-q", "-m", message], cwd=dest, env=env)

    # REVERSED: the specs' first-commit dates must run *opposite* to their path order, or
    # `created` and the `(source path, index)` tie-break would agree and a test could not
    # tell an allocation keyed on real dates from one keyed on nothing.
    spec_rels = [p.relative_to(dest).as_posix() for p in reversed(specs)]
    _git(["add", "-A"], cwd=dest)
    for rel in spec_rels:
        _git(["reset", "--quiet", "--", rel], cwd=dest)
    _commit([], 1, "seed: everything but the specs")
    for i, rel in enumerate(spec_rels):
        _commit([rel], 2 + i, f"add {rel}")
    return dest


def _tree_files(root: pathlib.Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file() and ".git" not in path.parts
    }


# =========================================================================================
# 1. The refusal, on deliberately broken input — by name, in both failure shapes.
# =========================================================================================


def test_a_plain_directory_is_refused_by_name(
    doc_id_cli: Any, tmp_path: pathlib.Path
) -> None:
    root = tmp_path / "tree"
    (root / "docs" / "specs").mkdir(parents=True)
    spec = root / "docs" / "specs" / "00-overview.md"
    spec.write_text("# overview\n", encoding="utf-8")

    with pytest.raises(doc_id_cli.GitHistoryUnavailableError) as excinfo:
        doc_id_cli._module_first_commit_date(spec, root)

    message = str(excinfo.value)
    # It names the path, the tree, the measured provenance, and what to do about it.
    assert "docs/specs/00-overview.md" in message
    assert str(root) in message
    assert "rev-list --count HEAD = 0" in message
    assert "is-shallow-repository = false" in message
    assert "DECLARED INPUT" in message
    assert "DOCID_FIXTURE_CREATED_DATE" in message


def test_a_shallow_clone_is_refused_by_name(
    doc_id_cli: Any, tmp_path: pathlib.Path
) -> None:
    """A shallow clone's failure is the dangerous one: it answers, and the answer is wrong.

    `git log --diff-filter=A --follow` in a shallow clone returns the shallow boundary
    commit, so the old code would have taken a real, well-formed date that is not the
    file's first-commit date. Nothing downstream could notice.
    """
    source = _multi_day_repo(tmp_path / "source")
    shallow = tmp_path / "shallow"
    _git(
        ["clone", "--quiet", "--depth", "1", f"file://{source}", str(shallow)],
        cwd=tmp_path,
    )
    doc_id_cli._root_is_shallow.cache_clear()
    assert doc_id_cli.is_shallow_repository(shallow) is True

    spec = sorted((shallow / "docs" / "specs").glob("*.md"))[0]
    # Not vacuous: git *does* hand back a date here. The refusal is what rejects it.
    assert _git(
        ["log", "--diff-filter=A", "--follow", "--format=%aI", "--",
         spec.relative_to(shallow).as_posix()],
        cwd=shallow,
    ).strip()

    with pytest.raises(doc_id_cli.GitHistoryUnavailableError) as excinfo:
        doc_id_cli._module_first_commit_date(spec, shallow)

    message = str(excinfo.value)
    assert "shallow clone" in message
    assert "wrong date, not a missing one" in message
    assert "is-shallow-repository = true" in message
    assert spec.name in message


def test_a_declared_fixture_date_satisfies_the_refusal(
    doc_id_cli: Any, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The escape hatch is explicit, and it is not the wall clock.

    Without this, the refusal would be unusable for the `tmp_path` fixture corpora that
    legitimately have no history — and the pressure would be to reinstate the silent
    substitution rather than declare the date.
    """
    root = tmp_path / "tree"
    (root / "docs" / "specs").mkdir(parents=True)
    spec = root / "docs" / "specs" / "00-overview.md"
    spec.write_text("# overview\n", encoding="utf-8")

    monkeypatch.setenv("DOCID_FIXTURE_CREATED_DATE", "2019-03-14")
    assert doc_id_cli._module_first_commit_date(spec, root) == datetime.date(2019, 3, 14)
    assert doc_id_cli._module_first_commit_date(spec, root) != datetime.date.today()


def test_a_malformed_declared_fixture_date_is_refused_rather_than_ignored(
    doc_id_cli: Any, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "tree"
    (root / "docs" / "specs").mkdir(parents=True)
    spec = root / "docs" / "specs" / "00-overview.md"
    spec.write_text("# overview\n", encoding="utf-8")

    monkeypatch.setenv("DOCID_FIXTURE_CREATED_DATE", "14/03/2019")
    with pytest.raises(doc_id_cli.GitHistoryUnavailableError, match="is not an ISO date"):
        doc_id_cli._module_first_commit_date(spec, root)


# =========================================================================================
# 2. `git archive` + `git init` — the old snapshot construction — no longer allocates.
# =========================================================================================


def _archive_and_init(doc_id_cli: Any, ref: str, source: pathlib.Path,
                      dest: pathlib.Path) -> pathlib.Path:
    """`_docverify._materialise`'s construction as it stood before PR-A."""
    dest.mkdir(parents=True, exist_ok=True)
    doc_id_cli.materialize_ref(ref, dest, repo_root=source)
    _git(["init", "-q", "-b", "snapshot"], cwd=dest)
    _git(["config", "user.email", "t@t"], cwd=dest)
    _git(["config", "user.name", "Test"], cwd=dest)
    _git(["add", "-A"], cwd=dest)
    _git(["-c", "commit.gpgsign=false", "commit", "-q", "-m", "snapshot"], cwd=dest)
    return dest


def test_archive_and_init_allocates_differently_from_a_real_history_clone(
    doc_id_cli: Any, tmp_path: pathlib.Path
) -> None:
    """The defect, demonstrated rather than asserted — and a correction to how it was
    described to me.

    The brief for this work said the archive-and-init snapshot fell through
    `_module_first_commit_date`'s `date.today()` fallback. **It does not, and could not.**
    `git init` + `git add -A` + `git commit` gives every file a perfectly valid adding
    commit, so `git log --diff-filter=A --follow` succeeds and returns *the synthetic
    commit's* date. The route is different; the effect is identical and worse for being
    well-formed — every draft takes one date, the sort collapses onto the `(source path,
    index)` tie-break, and the allocation silently stops being a function of chronology.

    So no refusal can catch this shape, and none is claimed to: the fix is that the
    instrument no longer *builds* it (see the test below). What this test pins is that the
    two constructions genuinely disagree — without which every other test here could pass
    with history doing no work at all.
    """
    source = _multi_day_repo(tmp_path / "source")

    with_history = tmp_path / "with-history"
    doc_id_cli.materialize_ref_with_history("HEAD", with_history, repo_root=source)
    doc_id_cli._root_is_shallow.cache_clear()
    real = doc_id_cli.migrate(with_history)

    snapshot = _archive_and_init(doc_id_cli, "HEAD", source, tmp_path / "archive-init")
    doc_id_cli._root_is_shallow.cache_clear()
    synthetic = doc_id_cli.migrate(snapshot)

    assert real.assigned
    assert synthetic.assigned
    assert real.assigned != synthetic.assigned, (
        "history is not load-bearing in this corpus — the two constructions agree, so "
        "nothing else in this module is testing what it claims to test"
    )


def test_the_instrument_no_longer_builds_a_history_less_snapshot(
    doc_id_cli: Any, tmp_path: pathlib.Path
) -> None:
    """`_docverify._materialise` is the one place the snapshot's shape is decided, so it is
    the one place worth pinning: whatever it builds carries the source's full history."""
    docverify = _load_docverify()

    source = _multi_day_repo(tmp_path / "source")
    dest = tmp_path / "built"
    docverify._materialise(doc_id_cli, "HEAD", dest, repo_root=source)

    expected = doc_id_cli.history_commit_count(source)
    assert expected > 1
    assert doc_id_cli.history_commit_count(dest) == expected
    assert doc_id_cli.is_shallow_repository(dest) is False


def test_materialize_ref_preserves_the_exec_bit(
    doc_id_cli: Any, tmp_path: pathlib.Path
) -> None:
    """`ZipFile.extractall` drops mode bits, so an extracted tree differed from the
    committed one in a way no content comparison would ever see."""
    source = tmp_path / "source"
    source.mkdir()
    _git(["init", "--initial-branch=main", "--quiet"], cwd=source)
    _git(["config", "user.email", "t@t"], cwd=source)
    _git(["config", "user.name", "Test"], cwd=source)
    script = source / "run.sh"
    script.write_text("#!/bin/sh\necho hi\n", encoding="utf-8")
    script.chmod(0o755)
    plain = source / "plain.md"
    plain.write_text("hi\n", encoding="utf-8")
    _git(["add", "-A"], cwd=source)
    _git(["-c", "commit.gpgsign=false", "commit", "-q", "-m", "seed"], cwd=source)

    dest = tmp_path / "dest"
    dest.mkdir()
    doc_id_cli.materialize_ref("HEAD", dest, repo_root=source)
    assert (dest / "run.sh").stat().st_mode & 0o111, "exec bit lost by materialisation"
    assert not (dest / "plain.md").stat().st_mode & 0o111


# =========================================================================================
# 3. The acceptance test: two materialisations, one ref, different days.
# =========================================================================================


class _ShiftedClock(datetime.date):
    """`date`, with `today()` answering a date years from now."""

    @classmethod
    def today(cls) -> _ShiftedClock:
        return cls(2031, 12, 31)


class _NoClock(datetime.date):
    """`date`, with `today()` refusing to answer at all."""

    @classmethod
    def today(cls) -> _NoClock:
        raise AssertionError(
            "the migration read the wall clock — its output is not a function of the ref"
        )


def test_two_materialisations_of_one_ref_allocate_identically_on_different_days(
    doc_id_cli: Any, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = _multi_day_repo(tmp_path / "source")

    first = tmp_path / "first"
    doc_id_cli.materialize_ref_with_history("HEAD", first, repo_root=source)
    doc_id_cli._root_is_shallow.cache_clear()
    result_first = doc_id_cli.migrate(first)

    second = tmp_path / "second"
    doc_id_cli.materialize_ref_with_history("HEAD", second, repo_root=source)
    doc_id_cli._root_is_shallow.cache_clear()
    # THE TRAP, disarmed: without this the two runs share a wall clock and the comparison
    # goes green with the defect fully present.
    monkeypatch.setattr(doc_id_cli, "date", _ShiftedClock)
    result_second = doc_id_cli.migrate(second)

    assert result_first.assigned, "vacuous: nothing was allocated at all"
    assert result_first.assigned == result_second.assigned
    files_first, files_second = _tree_files(first), _tree_files(second)
    assert set(files_first) == set(files_second)
    differing = sorted(rel for rel in files_first if files_first[rel] != files_second[rel])
    assert differing == [], f"output moved with the calendar: {differing}"


def test_the_migration_completes_with_the_wall_clock_unreadable(
    doc_id_cli: Any, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The strongest form of the same claim: not "the same answer on two days" but "the
    clock was never read". A shifted clock proves the output does not *move*; a clock that
    raises proves there is nothing left to move it.
    """
    source = _multi_day_repo(tmp_path / "source")
    tree = tmp_path / "tree"
    doc_id_cli.materialize_ref_with_history("HEAD", tree, repo_root=source)
    doc_id_cli._root_is_shallow.cache_clear()
    monkeypatch.setattr(doc_id_cli, "date", _NoClock)
    result = doc_id_cli.migrate(tree)
    assert result.assigned


def test_a_clone_at_a_ref_carries_the_full_history_and_no_remotes(
    doc_id_cli: Any, tmp_path: pathlib.Path
) -> None:
    """The provenance fields the run records — `rev-list --count` and
    `is-shallow-repository` — measured on the materialisation itself."""
    source = _multi_day_repo(tmp_path / "source")
    expected = doc_id_cli.history_commit_count(source)
    assert expected > 1, "vacuous: the source has no history to lose"

    dest = tmp_path / "dest"
    doc_id_cli.materialize_ref_with_history("HEAD", dest, repo_root=source)
    assert doc_id_cli.history_commit_count(dest) == expected
    assert doc_id_cli.is_shallow_repository(dest) is False
    assert _git(["remote"], cwd=dest).strip() == ""
    assert (
        _git(["rev-parse", "HEAD"], cwd=dest).strip()
        == _git(["rev-parse", "HEAD"], cwd=source).strip()
    )


def test_a_shallow_source_repository_is_refused_at_materialisation(
    doc_id_cli: Any, tmp_path: pathlib.Path
) -> None:
    source = _multi_day_repo(tmp_path / "source")
    shallow = tmp_path / "shallow"
    _git(
        ["clone", "--quiet", "--depth", "1", f"file://{source}", str(shallow)],
        cwd=tmp_path,
    )
    with pytest.raises(doc_id_cli.GitArchiveError, match="shallow"):
        doc_id_cli.materialize_ref_with_history("HEAD", tmp_path / "dest", repo_root=shallow)
