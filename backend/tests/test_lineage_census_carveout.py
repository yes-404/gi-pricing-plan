"""RL-949's `generated_from_tracked_corpus` carve-out — the broken-input proof.

`docs/rulings/RL-00949-rfc-897-slice-2-s-census-csv-and-fr-72-the-test-is-overbroad-the.md` §4: `CLAUDE.md` §13 requires a
carve-out that has never printed a failure to be treated as untested, and the positive
control must exercise the same predicate the guard fires on, not an easier case. These tests
run against a synthetic git repository built in `tmp_path` — mirroring `tests/test_file_
census.py`'s own synthetic-tree pattern — never against this repository's own tree: the live
`test_no_reference_rows_are_bundled_in_the_repository`
(`backend/tests/test_lineage.py`) is an integration-style sweep over the real checkout and
cannot host a deliberately-broken fixture inside itself, and the real repository's history
must not be mutated to manufacture a bad commit.

Three cases, all required by §4:

  - a positive control (a genuine census, matching its named tree, is exempted);
  - mismatched content naming a *resolvable* commit (still caught — this is what makes the
    carve-out not a bare allowlist);
  - an unresolvable commit (the test itself fails, naming the SHA — never a silent
    exemption; this is the "carve-out satisfied by absence" failure mode §3 point 2 names).

`generated_from_tracked_corpus` and `resolve_commit` are imported from `test_lineage`, not
reimplemented, so this proof exercises the exact function the live sweep calls.
"""

from __future__ import annotations

import pathlib
import subprocess

import pytest
from backend.tests.test_lineage import (
    CENSUS_CSV_HEADER,
    generated_from_tracked_corpus,
    resolve_commit,
)


def _run_git(root: pathlib.Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=True,
    )


def _init_repo(root: pathlib.Path, files: dict[str, str]) -> str:
    """Create a synthetic git repository at `root`, commit `files`, and return the full SHA."""
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=root, check=True)
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "seed"], cwd=root, check=True)
    return _run_git(root, "rev-parse", "HEAD").stdout.strip()


def _write_census(root: pathlib.Path, sha: str, rows: list[str]) -> pathlib.Path:
    """Write `docs/audit/file-census-<short sha>.csv` at `root`, matching the registered
    pattern (`backend/tests/test_lineage.py`'s `GENERATED_CORPUS_REGISTRY`)."""
    census = root / "docs" / "audit" / f"file-census-{sha[:7]}.csv"
    census.parent.mkdir(parents=True, exist_ok=True)
    lines = [CENSUS_CSV_HEADER, *rows]
    census.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return census


@pytest.fixture
def synthetic_repo(tmp_path: pathlib.Path) -> pathlib.Path:
    root = tmp_path / "repo"
    root.mkdir()
    return root


# -- positive control -----------------------------------------------------------------------


def test_a_genuine_census_matching_its_named_tree_is_exempted(
    synthetic_repo: pathlib.Path,
) -> None:
    """§4's positive control: a file whose name matches the registered pattern and whose
    `path` column, sorted, genuinely equals `git ls-tree -r --name-only <sha>`, sorted, at a
    real commit in the fixture repo's own history is exempted."""
    sha = _init_repo(
        synthetic_repo,
        {
            "README.md": "root readme",
            "docs/specs/00-overview.md": "a spec",
            "scripts/tool.py": "print('hi')",
        },
    )
    tracked = sorted(_run_git(synthetic_repo, "ls-tree", "-r", "--name-only", sha)
                      .stdout.splitlines())
    assert tracked == ["README.md", "docs/specs/00-overview.md", "scripts/tool.py"]

    rows = [f"{path},,,0,unknown,0" for path in tracked]
    census = _write_census(synthetic_repo, sha, rows)

    assert generated_from_tracked_corpus(census, synthetic_repo) is True


# -- mismatched content, resolvable SHA ------------------------------------------------------


def test_mismatched_content_naming_a_resolvable_commit_is_not_exempted(
    synthetic_repo: pathlib.Path,
) -> None:
    """§4's second case: a file matching the registered pattern, naming a commit that *does*
    resolve, but whose `path` column diverges from that commit's `git ls-tree` — e.g. rows
    describing a bundled reference-set file that was never in the named tree — is not
    exempted, and the whole-tree sweep would still report it."""
    sha = _init_repo(
        synthetic_repo,
        {
            "README.md": "root readme",
            "docs/specs/00-overview.md": "a spec",
        },
    )
    # Simulates bundled reference data spliced into the census — the exact shape a real
    # ABI/ONS drop, or the "current tree" mistake §3 point 2 corrects, would produce.
    rows = [
        "README.md,,,0,unknown,0",
        "docs/specs/00-overview.md,,,0,living,0",
        "docs/audit/abi-vehicle-groups.csv,,,0,unknown,0",
    ]
    census = _write_census(synthetic_repo, sha, rows)

    assert generated_from_tracked_corpus(census, synthetic_repo) is False


def test_a_dropped_row_naming_a_resolvable_commit_is_not_exempted(
    synthetic_repo: pathlib.Path,
) -> None:
    """Same shape, the other direction: fewer rows than the named tree also fails exact
    list equality — a set comparison would hide this (§3 point 2's second-to-last bullet)."""
    sha = _init_repo(
        synthetic_repo,
        {
            "README.md": "root readme",
            "docs/specs/00-overview.md": "a spec",
        },
    )
    rows = ["README.md,,,0,unknown,0"]  # missing docs/specs/00-overview.md
    census = _write_census(synthetic_repo, sha, rows)

    assert generated_from_tracked_corpus(census, synthetic_repo) is False


def test_a_registered_filename_pattern_alone_grants_nothing(
    synthetic_repo: pathlib.Path,
) -> None:
    """§3 point 4, stated as its own assertion: a reviewer should be able to construct a
    file that matches the registered pattern and is real reference data, and watch the
    exemption refuse it. Filename-pattern match alone (point 1) only makes a file a
    *candidate* — it never itself grants the exemption."""
    sha = _init_repo(synthetic_repo, {"README.md": "root readme"})
    # Header itself is wrong (real reference-set data would not be file-census output) —
    # the exemption must not fire on filename alone even before the path column is checked.
    census_dir = synthetic_repo / "docs" / "audit"
    census_dir.mkdir(parents=True, exist_ok=True)
    fake = census_dir / f"file-census-{sha[:7]}.csv"
    fake.write_text("group_code,make,model,rating_group\nA1,Ford,Fiesta,12\n", encoding="utf-8")

    assert generated_from_tracked_corpus(fake, synthetic_repo) is False


# -- unresolvable SHA -------------------------------------------------------------------------


def test_an_unresolvable_sha_fails_outright_naming_the_sha(
    synthetic_repo: pathlib.Path,
) -> None:
    """§4's third case: a file matching the registered pattern but naming a commit absent
    from the fixture repo and unreachable by fetch (no `origin` remote configured) causes
    `generated_from_tracked_corpus` itself to fail, naming the unresolved SHA — never a
    silent exemption and never a silent pass-through."""
    _init_repo(synthetic_repo, {"README.md": "root readme"})
    unresolvable_sha = "deadbeef00" * 4  # well-formed 40-hex, absent from history and remote
    rows = ["README.md,,,0,unknown,0"]
    census = _write_census(synthetic_repo, unresolvable_sha, rows)

    # The registered pattern's capture group is the exact sha the filename carries — here,
    # the 7-char short form `_write_census` names the file with (real convention: the
    # committed CSV is `file-census-5ef559d.csv`, a 7-char short sha). The failure message
    # must name that sha so a reader can act on it without decoding the filename first.
    short_sha = unresolvable_sha[:7]
    with pytest.raises(AssertionError, match=short_sha):
        generated_from_tracked_corpus(census, synthetic_repo)


def test_resolve_commit_returns_none_rather_than_raising_for_an_unresolvable_sha(
    synthetic_repo: pathlib.Path,
) -> None:
    """`resolve_commit` itself (used directly by `generated_from_tracked_corpus`) returns
    `None` rather than raising — the caller decides what that means, per its docstring."""
    _init_repo(synthetic_repo, {"README.md": "root readme"})
    assert resolve_commit(synthetic_repo, "deadbeef00" * 4) is None


def test_resolve_commit_resolves_a_real_commit_locally(synthetic_repo: pathlib.Path) -> None:
    sha = _init_repo(synthetic_repo, {"README.md": "root readme"})
    assert resolve_commit(synthetic_repo, sha) == sha
    assert resolve_commit(synthetic_repo, sha[:7]) == sha


def test_resolve_commit_fetches_from_a_remote_when_local_resolution_fails(
    tmp_path: pathlib.Path,
) -> None:
    """The shallow-checkout case RL-949 §3 point 2 is written for: the ancestor SHA is
    unresolvable in a shallow clone until an explicit `git fetch --depth 1 origin <sha>`
    retrieves it. Built with a real `origin` remote (a `file://` clone of a source repo with
    a second commit the shallow clone never sees) so this exercises the actual fetch path,
    not just its absence."""
    source = tmp_path / "source"
    source.mkdir()
    first_sha = _init_repo(source, {"README.md": "v1"})
    (source / "README.md").write_text("v2", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=source, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "second"], cwd=source, check=True)

    shallow = tmp_path / "shallow"
    subprocess.run(
        ["git", "clone", "-q", "--depth", "1", f"file://{source}", str(shallow)], check=True,
    )
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=shallow, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=shallow, check=True)

    # Confirms the premise: the shallow clone genuinely cannot resolve the older commit yet.
    unverified = subprocess.run(
        ["git", "-C", str(shallow), "rev-parse", "--quiet", "--verify", f"{first_sha}^{{commit}}"],
        capture_output=True, text=True, check=False,
    )
    assert unverified.returncode != 0

    assert resolve_commit(shallow, first_sha) == first_sha
