"""Tests for `scripts/double-stamp-scan.py` — proving each net fires.

**Why these exist.** At every tree measured so far the scan returns `second_block: 0`, and
`CLAUDE.md` §13 is explicit that a check which has never printed a failure has not been
tested, only written. The scan's whole value is that it can distinguish a *completed*
migration from a *correct* one; a scan that cannot fire distinguishes nothing.

Every case is built in `tmp_path`. The real tree is never mutated — that is `F89` limb 1
declined rather than repeated, the same discipline `tests/test_findings_ids.py` states.

No `@pytest.mark.req` marker: this is correctness of a verification tool, not evidence for
a numbered platform requirement — the reasoning `tests/test_doc_id.py`'s module docstring
gives for the same choice.
"""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys
import types

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCAN_PATH = ROOT / "scripts" / "double-stamp-scan.py"

if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))


@pytest.fixture(scope="module")
def scan() -> types.ModuleType:
    """The identical by-path loader the other script tests use, for the identical reason:
    a hyphenated filename is not an `import` target."""
    spec = importlib.util.spec_from_file_location("_double_stamp_scan_under_test", SCAN_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


#: Exactly what the migration's prepending writers produce over a file that already had
#: front matter: `write_text(header + "\n" + body)` where `body` still opens with `---`.
DOUBLE_STAMPED = (
    "---\n"
    "family: reference\n"
    "title: example\n"
    "status: active\n"
    "owner: maintainer\n"
    "---\n"
    "\n"
    "---\n"
    "name: example\n"
    "description: the harness's own block, demoted into the body\n"
    "---\n"
    "\n"
    "# Example\n"
)

SINGLE_STAMPED = (
    "---\n"
    "family: reference\n"
    "title: example\n"
    "status: active\n"
    "owner: maintainer\n"
    "---\n"
    "\n"
    "# Example\n"
)


def test_second_block_fires_on_a_double_stamped_file(
    scan: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """The signature net, on the exact byte pattern a prepending writer produces.

    This is the case three other instruments read as correct: `_docid.parse_header` parses
    the leading block cleanly, its `.extra` is empty so check 30 has nothing to object to,
    and `_front_matter_state` returns `"stamped"` so a second run skips it.
    """
    (tmp_path / "doubled.md").write_text(DOUBLE_STAMPED, encoding="utf-8")
    (tmp_path / "fine.md").write_text(SINGLE_STAMPED, encoding="utf-8")
    nets = scan.scan_tree(tmp_path)
    assert nets["second_block"] == ["doubled.md"]
    assert "fine.md" not in nets["second_block"]


def test_the_three_instruments_this_net_exists_to_outvote_all_read_it_as_correct(
    scan: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """The premise of the whole script, asserted rather than described.

    If `parse_header` choked on a double-stamped file, or `_front_matter_state` called it
    `"foreign"`, this scan would be redundant with checks that already run. It is not:
    both read the corruption as a valid stamp, which is why the tree has to be read.
    """
    docid = sys.modules.get("_docid") or scan._docid
    doc_id_cli = _load_doc_id()
    path = tmp_path / "doubled.md"
    path.write_text(DOUBLE_STAMPED, encoding="utf-8")

    header = docid.parse_header(path)
    assert header is not None, "parse_header rejects it — this net would be redundant"
    assert header.family == "reference"
    assert dict(header.extra) == {}, "an unknown field would give check 30 something to catch"
    assert doc_id_cli._front_matter_state(path.read_text(encoding="utf-8")) == "stamped"


def _load_doc_id() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(
        "_doc_id_for_scan_test", ROOT / "scripts" / "doc-id.py"
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_harness_below_fires_and_names_its_false_positive_class(
    scan: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """The broad net fires on a demoted harness block **and** on a document that merely
    quotes one — which is why its hits are resolved against a baseline, never read alone.
    """
    (tmp_path / "doubled.md").write_text(DOUBLE_STAMPED, encoding="utf-8")
    (tmp_path / "about-front-matter.md").write_text(
        SINGLE_STAMPED + "\nAn example block:\n\nname: illustrative\ndescription: quoted\n",
        encoding="utf-8",
    )
    nets = scan.scan_tree(tmp_path)
    assert set(nets["harness_below"]) == {"doubled.md", "about-front-matter.md"}
    # And the precise net separates them, which is the whole point of reporting both.
    assert nets["second_block"] == ["doubled.md"]


def test_gt2_delims_is_a_superset_that_catches_thematic_breaks(
    scan: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """The broadest net, and the reason it is never reported as a count: a markdown
    horizontal rule in the body trips it on a perfectly correct file."""
    (tmp_path / "rules.md").write_text(
        SINGLE_STAMPED + "\nfirst section\n\n---\n\nsecond section\n", encoding="utf-8"
    )
    nets = scan.scan_tree(tmp_path)
    assert nets["gt2_delims"] == ["rules.md"]
    assert nets["second_block"] == []
    assert nets["harness_below"] == []


def test_changed_since_intersection_excludes_a_file_the_run_never_wrote(
    scan: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """A file the run never wrote cannot have been double-stamped by the run."""
    (tmp_path / "doubled.md").write_text(DOUBLE_STAMPED, encoding="utf-8")
    assert scan.scan_tree(tmp_path, limit_to={"doubled.md"})["second_block"] == ["doubled.md"]
    assert scan.scan_tree(tmp_path, limit_to=set())["second_block"] == []


def test_changed_since_sees_an_untracked_created_file(
    scan: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """The regression that shipped: `--changed-since` must see files git is not tracking.

    `git diff --name-only <ref>` reports **tracked files only**. The migration's stamp
    writers create new drafts, which are untracked until someone commits them — so the
    original filter was blind to precisely the population a double-stamp would appear in.
    Measured on one tree with one injected defect: whole-tree gave `second_block 1` and
    exit 1, `--changed-since main` gave `second_block 0` and **exit 0**. A filter that
    returns a clean signature on a tree carrying the defect is worse than no filter.

    Built as a real git repository in `tmp_path` rather than mocked, because the defect was
    in what `git diff` reports and a mock would have been written to the same wrong belief.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    def run(*args: str) -> None:
        """Typed rather than a lambda: `mypy --strict` covers `tests/`, and a bare
        `lambda *a:` is an untyped function whose every call it rejects."""
        subprocess.run(args, cwd=repo, check=True, capture_output=True, text=True)

    run("git", "init", "--initial-branch=main", "-q")
    run("git", "config", "user.email", "t@example.com")
    run("git", "config", "user.name", "T")
    (repo / "tracked.md").write_text(SINGLE_STAMPED, encoding="utf-8")
    run("git", "add", "-A")
    run("git", "commit", "-qm", "base")

    # The created draft: untracked, and double-stamped — exactly the shape the migration
    # produces and the shape the old filter could not see.
    (repo / "created.md").write_text(DOUBLE_STAMPED, encoding="utf-8")

    changed = scan._changed_since(repo, "HEAD")
    assert "created.md" in changed, (
        "an untracked created file is invisible to `git diff --name-only`, which is the "
        "defect this test exists to prevent"
    )
    assert scan.scan_tree(repo, changed)["second_block"] == ["created.md"]
    assert scan.main([str(repo), "--changed-since", "HEAD"]) == 1


def test_leading_block_reads_only_the_first_block(scan: types.ModuleType) -> None:
    """`leading_block` must stop at the first closing `---`, or a double-stamped file and
    its clean original would compare equal and the vendored check would pass on a stamp."""
    assert scan.leading_block(DOUBLE_STAMPED) == (
        "---\nfamily: reference\ntitle: example\nstatus: active\nowner: maintainer\n---"
    )
    assert scan.leading_block(DOUBLE_STAMPED) != scan.leading_block(
        "---\nname: example\ndescription: the harness's own block, demoted into the body\n---\n"
    )
    assert scan.leading_block("# no front matter\n") is None
    assert scan.leading_block("---\nunterminated: true\n") is None


def test_main_exits_nonzero_only_when_the_signature_net_fires(
    scan: types.ModuleType, tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The broad nets must not fail a run on their own — a thematic break is not a defect."""
    clean = tmp_path / "clean"
    clean.mkdir()
    (clean / "rules.md").write_text(
        SINGLE_STAMPED + "\nbody\n\n---\n\nmore\n", encoding="utf-8"
    )
    assert scan.main([str(clean)]) == 0

    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "doubled.md").write_text(DOUBLE_STAMPED, encoding="utf-8")
    assert scan.main([str(bad)]) == 1
    assert "doubled.md" in capsys.readouterr().out


def test_the_real_tree_is_clean_on_the_signature_net(scan: types.ModuleType) -> None:
    """The control the mutations above are read against, and a live claim about this
    checkout: nothing here carries two front-matter blocks."""
    nets = scan.scan_tree(ROOT)
    assert nets["second_block"] == [], nets["second_block"]
