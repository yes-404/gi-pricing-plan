"""`scripts/file-census.py` — Stage 0 evidence for NT-0016 (Q1, Q2, Q3).

`docs/plans/2026-08-31-nt-0016-investigation.md` §7 (Slice 2). These tests run against a
synthetic git repository built in `tmp_path`, never against this repository's own tree — the
repository's numbers move (the next merge adds or removes files), and a test pinned to a
live count fails for a reason unrelated to the code under test.

Step 5 of §7 requires the broken-input proof — a non-git directory must exit non-zero naming
the cause rather than emit an empty CSV, because an empty census is indistinguishable from a
clean repository and would be committed as evidence of one; that proof lives here as
`test_non_git_root_exits_non_zero_naming_the_cause` and is also run manually against a real
temp directory as part of the slice's acceptance evidence.

No `@pytest.mark.req` marker: this is correctness of the census tool itself, not evidence
for a numbered platform requirement — the same reasoning `tests/test_register_lint.py`,
`tests/test_scope_audit.py` and `tests/test_audit_docs_finding_citations.py` give for their
own scripts.
"""

from __future__ import annotations

import csv
import importlib.util
import io
import pathlib
import subprocess
import sys
from typing import cast

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "file-census.py"

# `scripts/file-census.py` has a hyphen and is not importable by name (plan §7 Step 2) — load
# it by path, the same way `tests/test_register_lint.py` loads `scripts/register-lint.py`.
#
# The explicit `SCRIPT.exists()` check below is deliberate, not decorative: without it, a
# missing script makes `spec_from_file_location` + `exec_module` raise `FileNotFoundError`
# (verified empirically — `spec_from_file_location` does not check existence at spec-creation
# time, only `exec_module`'s `get_data` does, at load time), not `ImportError` /
# `ModuleNotFoundError`. Plan §7 Step 2 requires the pre-implementation failure to be
# "ImportError / ModuleNotFoundError naming file_census ... A failure with any other cause
# means the import path is wrong, not that the test is correct" — so the check exists to make
# that true, not to be defensive for its own sake.
if not SCRIPT.exists():
    raise ModuleNotFoundError(f"No module named 'file_census': not found at {SCRIPT}")
_spec = importlib.util.spec_from_file_location("_file_census_under_test", SCRIPT)
assert _spec is not None
assert _spec.loader is not None
file_census = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = file_census  # dataclasses needs the module in sys.modules
_spec.loader.exec_module(file_census)


# --- the plan's two literal test bodies (§7 Step 1) -------------------------------------


def test_name_pattern_normalises_dates_then_digits() -> None:
    assert (
        file_census.name_pattern("2026-08-29-w11-3-batch-scoring.md")
        == "DATE-wN-N-batch-scoring.md"
    )
    assert file_census.name_pattern("0016-file-taxonomy.md") == "N-file-taxonomy.md"


def test_referenced_by_excludes_the_file_itself() -> None:
    texts = {"a.md": "see b.md", "b.md": "b.md is me"}
    assert file_census.referenced_by("b.md", texts) == 1


# --- name_pattern, more shapes -----------------------------------------------------------


def test_name_pattern_with_no_digits_is_unchanged() -> None:
    assert file_census.name_pattern("README.md") == "README.md"


def test_name_pattern_date_not_at_start() -> None:
    assert file_census.name_pattern("register-2026-08-30-notes.md") == "register-DATE-notes.md"


def test_name_pattern_multiple_digit_runs() -> None:
    assert file_census.name_pattern("v1.2.3-final.txt") == "vN.N.N-final.txt"


# --- referenced_by, more shapes -----------------------------------------------------------


def test_referenced_by_zero_when_nothing_mentions_it() -> None:
    texts = {"a.md": "nothing here", "orphan.md": "also nothing"}
    assert file_census.referenced_by("orphan.md", texts) == 0


def test_referenced_by_same_basename_different_directory_not_self_excluded() -> None:
    # Two files share a basename in different directories. Excluding "the file itself" is
    # by full path, not by basename, so the sibling can still count as a reference.
    texts = {
        "dir1/x.md": "no mention",
        "dir2/x.md": "see x.md over there",
    }
    assert file_census.referenced_by("dir1/x.md", texts) == 1
    # And the target's own content is excluded even though it also contains its basename.
    texts_self_mention = {"dir1/x.md": "this file is x.md"}
    assert file_census.referenced_by("dir1/x.md", texts_self_mention) == 0


def test_referenced_by_counts_multiple_referrers() -> None:
    texts = {
        "target.md": "content",
        "a.md": "mentions target.md",
        "b.md": "also mentions target.md",
        "c.md": "unrelated",
    }
    assert file_census.referenced_by("target.md", texts) == 2


# --- area / mutability ---------------------------------------------------------------------


def test_area_is_first_path_segment() -> None:
    assert file_census.area("docs/specs/01-data-management.md") == "docs"
    assert file_census.area("README.md") == "README.md"


@pytest.mark.parametrize(
    ("rel_path", "expected"),
    [
        ("docs/plans/2026-08-31-nt-0016-investigation.md", "frozen"),
        ("docs/audit/work/some-task.md", "frozen"),
        ("docs/contracts/openapi/generated.json", "generated"),
        ("docs/specs/00-overview.md", "living"),
        ("docs/process/delivery-process.md", "living"),
        ("scripts/file-census.py", "unknown"),
        (".claude/skills/README.md", "unknown"),
        ("docs/audit/register.md", "unknown"),  # docs/audit/ itself, not docs/audit/work/
    ],
)
def test_mutability_directory_prefix_rules(rel_path: str, expected: str) -> None:
    assert file_census.mutability(rel_path) == expected


# --- CSV shape -------------------------------------------------------------------------


def test_csv_header_is_exact() -> None:
    assert file_census.CSV_HEADER == [
        "path",
        "area",
        "name_pattern",
        "size_bytes",
        "mutability",
        "referenced_by",
    ]


def test_write_csv_round_trips_a_row() -> None:
    row = file_census.Row(
        path="docs/specs/00-overview.md",
        area="docs",
        name_pattern="NN-overview.md",
        size_bytes=1234,
        mutability="living",
        referenced_by=3,
    )
    buf = io.StringIO()
    file_census.write_csv(buf, [row])
    buf.seek(0)
    reader = csv.DictReader(buf)
    assert reader.fieldnames == file_census.CSV_HEADER
    out_row = next(reader)
    assert out_row == {
        "path": "docs/specs/00-overview.md",
        "area": "docs",
        "name_pattern": "NN-overview.md",
        "size_bytes": "1234",
        "mutability": "living",
        "referenced_by": "3",
    }


# --- a synthetic git repository, end to end -----------------------------------------------


def _init_repo(root: pathlib.Path, files: dict[str, str]) -> None:
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=root, check=True)
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "seed"], cwd=root, check=True)


@pytest.fixture
def synthetic_repo(tmp_path: pathlib.Path) -> pathlib.Path:
    files = {
        "README.md": "root readme, does not mention the plan at all",
        "docs/plans/2026-08-01-x.md": "a frozen plan",
        "docs/specs/00-overview.md": "see docs/plans/2026-08-01-x.md for history",
        "docs/contracts/generated.json": '{"generated": true}',
        "docs/process/delivery-process.md": "the process",
        "scripts/tool.py": "print('hi')",
        "untracked-area/note.txt": "no directory rule covers this",
    }
    _init_repo(tmp_path, files)
    return tmp_path


def test_build_census_row_count_matches_git_ls_files(synthetic_repo: pathlib.Path) -> None:
    tracked = file_census.git_ls_files(synthetic_repo)
    rows = file_census.build_census(synthetic_repo, tracked)
    assert len(rows) == len(tracked)
    assert {r.path for r in rows} == set(tracked)


def test_build_census_mutability_and_referenced_by(synthetic_repo: pathlib.Path) -> None:
    tracked = file_census.git_ls_files(synthetic_repo)
    rows = {r.path: r for r in file_census.build_census(synthetic_repo, tracked)}

    assert rows["docs/plans/2026-08-01-x.md"].mutability == "frozen"
    assert rows["docs/contracts/generated.json"].mutability == "generated"
    assert rows["docs/specs/00-overview.md"].mutability == "living"
    assert rows["docs/process/delivery-process.md"].mutability == "living"
    assert rows["scripts/tool.py"].mutability == "unknown"
    assert rows["untracked-area/note.txt"].mutability == "unknown"

    # docs/specs/00-overview.md's content names the plan's basename.
    assert rows["docs/plans/2026-08-01-x.md"].referenced_by == 1
    assert rows["untracked-area/note.txt"].referenced_by == 0

    assert rows["untracked-area/note.txt"].area == "untracked-area"
    assert rows["README.md"].area == "README.md"


def test_main_writes_csv_to_out_file_with_one_row_per_tracked_file(
    synthetic_repo: pathlib.Path, tmp_path: pathlib.Path
) -> None:
    out = tmp_path / "census.csv"
    rc = file_census.main(["--root", str(synthetic_repo), "--out", str(out)])
    assert rc == 0
    tracked_count = len(file_census.git_ls_files(synthetic_repo))
    with out.open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        rows = list(reader)
    assert rows[0] == file_census.CSV_HEADER
    assert len(rows) - 1 == tracked_count


def test_main_reproduces_the_same_csv_byte_for_byte(
    synthetic_repo: pathlib.Path, tmp_path: pathlib.Path
) -> None:
    out1 = tmp_path / "one.csv"
    out2 = tmp_path / "two.csv"
    assert file_census.main(["--root", str(synthetic_repo), "--out", str(out1)]) == 0
    assert file_census.main(["--root", str(synthetic_repo), "--out", str(out2)]) == 0
    assert out1.read_bytes() == out2.read_bytes()


def test_main_summary_flag_does_not_change_the_csv(
    synthetic_repo: pathlib.Path, tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    plain = tmp_path / "plain.csv"
    summarised = tmp_path / "summarised.csv"
    assert file_census.main(["--root", str(synthetic_repo), "--out", str(plain)]) == 0
    assert (
        file_census.main(
            ["--root", str(synthetic_repo), "--out", str(summarised), "--summary"]
        )
        == 0
    )
    assert plain.read_bytes() == summarised.read_bytes()
    captured = capsys.readouterr()
    assert "per-area counts" in captured.err
    assert "per-name_pattern" in captured.err


# --- broken-input proof (§7 Step 5, required) --------------------------------------------


def test_git_ls_files_raises_naming_the_cause_for_a_non_git_directory(
    tmp_path: pathlib.Path,
) -> None:
    with pytest.raises(file_census.GitLsFilesError) as excinfo:
        file_census.git_ls_files(tmp_path)
    assert "git" in str(excinfo.value).lower()


def test_non_git_root_exits_non_zero_naming_the_cause(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The proof CLAUDE.md §13 requires: enforcement checked on deliberately broken input.

    A directory that is not a git repository must make `main()` exit non-zero with a
    message naming the cause on stderr — never emit an empty CSV, which would be silently
    indistinguishable from a genuinely clean repository.
    """
    rc = file_census.main(["--root", str(tmp_path)])
    captured = capsys.readouterr()
    assert rc != 0
    assert "git" in captured.err.lower()
    assert captured.out == ""  # no CSV — not even an empty header — was emitted


def test_cli_subprocess_non_git_root_exits_non_zero(tmp_path: pathlib.Path) -> None:
    """Same proof, run as a real subprocess against the actual script file rather than the
    in-process `main()` — closes the gap between "the function returns 1" and "the script,
    invoked the way an operator would invoke it, exits 1"."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "git" in result.stderr.lower()
    assert result.stdout == ""


def test_stdout_default_writes_csv_when_no_out_given(
    synthetic_repo: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rc = file_census.main(["--root", str(synthetic_repo)])
    assert rc == 0
    captured = capsys.readouterr()
    reader = csv.reader(io.StringIO(captured.out))
    rows = list(reader)
    assert rows[0] == file_census.CSV_HEADER
    assert len(rows) - 1 == len(file_census.git_ls_files(synthetic_repo))


def test_git_ls_files_type_is_list_of_str(synthetic_repo: pathlib.Path) -> None:
    tracked = file_census.git_ls_files(synthetic_repo)
    assert isinstance(tracked, list)
    assert all(isinstance(p, str) for p in cast("list[object]", tracked))
