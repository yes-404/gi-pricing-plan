"""Row (g) class 2, the wrap the migration's own reflow introduces (W37-6 PR-C).

PR #770 measured this live: on the reference tree, class 2 (`2-reference-token`) lost 23
files and `classified-by-none` gained 24 once `_reflow_long_lines` started running —
`_rewrite_citations` substitutes a citation with a longer, id-based path, and where that
substitution alone pushed the line over the project's limit, the reflow wraps it. The
content predicate class 2 shares with class 1/3 (`audit_docs.frozen_file_matches_after_
migration_stamp`) inverts the substitution with a *flat*, non-wrap-tolerant pattern
(`_inverse_token_pattern`), so a wrapped occurrence of the new token cannot be inverted
back to the old one and the comparison against the merge-base fails — a hunk that is
nothing but a reference-token substitution plus a wrap the migration itself introduced
then falls through Ruling 68's six classes to `classified-by-none`, a tool miss rather
than residue.

The fix reuses `_wrapped_path_patterns` — already defined and already the forward-
direction counterpart of the same wrap shape — to collapse a wrapped occurrence of a
known post-migration token back to contiguous before the ordinary flat inverse substitution
runs, in `classify_migration_diff`'s own `_classify_content`. Ruling 68's six classes are
unchanged; class 2 still means "a reference-token substitution", no wrap-tolerance rule is
reimplemented, and the deputy's placement (2026-09-06 10:34:53) applies: a fix, not a
ruling change.
"""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys
import types
from collections.abc import Sequence
from typing import Final

import pytest

ROOT: Final = pathlib.Path(__file__).resolve().parent.parent
DOC_ID_SCRIPT_PATH: Final = ROOT / "scripts" / "doc-id.py"

if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))


def _load_doc_id() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(
        "_doc_id_row_g_wrap_under_test", DOC_ID_SCRIPT_PATH
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def doc_id_cli() -> types.ModuleType:
    return _load_doc_id()


def _run_git(args: Sequence[str], *, cwd: pathlib.Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def _init_git(root: pathlib.Path) -> None:
    """`classify_migration_diff` shells out to `git ls-files` (via a second `migrate()`
    run) whenever it tries class 6, which every file in this fixture will, so `old_root`
    must be a real git repository — the identical requirement `test_doc_id_migrate.py`'s
    own `_init_git` states and the identical reason."""
    _run_git(["init", "--initial-branch=main", "--quiet"], cwd=root)
    _run_git(["config", "user.email", "test@example.com"], cwd=root)
    _run_git(["config", "user.name", "Test"], cwd=root)
    _run_git(["add", "-A"], cwd=root)
    _run_git(["commit", "-m", "seed", "--quiet"], cwd=root)


#: The shape #770 measured live: a citation to a path-shaped old token, substituted by
#: the migration for a longer, id-based new token, wrapped by `_reflow_long_lines`
#: after the substitution because the new token alone is longer than the line limit.
_OLD_TOKEN: Final = "docs/rulings/RL-00001-short.md"
_NEW_TOKEN: Final = (
    "docs/rulings/RL-00922-the-remediation-is-ruled-into-the-reopen-and-the-verdict-is-"
    "ruled-with-it-and-the-owner-named.md"
)

_REDIRECTS_CSV: Final = (
    "old_id,new_id,old_path,new_path,citing_dir\n"
    f"{_OLD_TOKEN},{_NEW_TOKEN},,,\n"
)


def test_reference_token_substitution_plus_migration_wrap_is_class2(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """A hunk that is nothing but a reference-token substitution, where the substitution
    itself pushed the citing line over the limit and the migration's own reflow wrapped
    it (the exact `# `-continuation shape `_wrapped_path_patterns`/`_reflow_line`
    produce), must classify class 2 — not `classified-by-none`.
    """
    old_root = tmp_path / "old"
    new_root = tmp_path / "new"
    rel = pathlib.Path("scripts") / "example.py"
    (old_root / rel.parent).mkdir(parents=True)
    (new_root / rel.parent).mkdir(parents=True)
    (old_root / rel).write_text(f"# see {_OLD_TOKEN} for background\nX = 1\n", encoding="utf-8")
    (new_root / rel).write_text(
        f"# see {_NEW_TOKEN.rsplit('-', 1)[0]}-\n"
        f"# {_NEW_TOKEN.rsplit('-', 1)[1]} for background\n"
        "X = 1\n",
        encoding="utf-8",
    )
    redirects = new_root / "docs" / "REDIRECTS.csv"
    redirects.parent.mkdir(parents=True, exist_ok=True)
    redirects.write_text(_REDIRECTS_CSV, encoding="utf-8")
    _init_git(old_root)

    classification = doc_id_cli.classify_migration_diff(old_root, new_root)

    rel_posix = rel.as_posix()
    assert rel_posix in classification.per_class["2-reference-token"], classification.summary()
    assert rel_posix not in classification.per_class[doc_id_cli.CLASSIFIED_BY_NONE]


def test_an_unrelated_wrap_still_falls_through_to_classified_by_none(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Control: a wrap that does NOT fall inside the substituted token — introduced by
    something other than the migration's own reflow of that citation — must still fail
    class 2 and fall through to `classified-by-none`, exactly as it did before this fix.
    The dewrap fallback only ever collapses a wrap `_wrapped_path_patterns` recognises as
    sitting inside one of `REDIRECTS.csv`'s own tokens; a wrap anywhere else is untouched.
    """
    old_root = tmp_path / "old"
    new_root = tmp_path / "new"
    rel = pathlib.Path("scripts") / "example.py"
    (old_root / rel.parent).mkdir(parents=True)
    (new_root / rel.parent).mkdir(parents=True)
    (old_root / rel).write_text(f"# see {_OLD_TOKEN} for background\nX = 1\n", encoding="utf-8")
    # The token substitutes cleanly and contiguously (a short new id here, not the long
    # one above), but a second, unrelated line was wrapped by something else entirely —
    # a hand edit, or any cause that is not this citation's own substitution.
    short_new_token = "docs/rulings/RL-00033-a-different-new-name.md"
    (new_root / rel).write_text(
        f"# see {short_new_token} for\n"
        "# background, unrelated to any citation token\n"
        "X = 1\n",
        encoding="utf-8",
    )
    redirects = new_root / "docs" / "REDIRECTS.csv"
    redirects.parent.mkdir(parents=True, exist_ok=True)
    redirects.write_text(
        "old_id,new_id,old_path,new_path,citing_dir\n"
        f"{_OLD_TOKEN},{short_new_token},,,\n",
        encoding="utf-8",
    )
    _init_git(old_root)

    classification = doc_id_cli.classify_migration_diff(old_root, new_root)

    rel_posix = rel.as_posix()
    assert rel_posix in classification.per_class[doc_id_cli.CLASSIFIED_BY_NONE], (
        classification.summary()
    )
    assert rel_posix not in classification.per_class["2-reference-token"]


# ---------------------------------------------------------------------------------------
# W37-6 PR-C loop 1 (measure `4d63810`): `_dewrap_reference_tokens` above only reaches a
# wrap inside a token that is both `/`-shaped and a literal key in `inverse`
# (`REDIRECTS.csv`-derived). Three residue causes `_docverify.py`'s own `_residue_cause`
# already names miss that test for a different reason each -- none rewritten by
# `REDIRECTS.csv` at all, so `inverse` never carries a matching key regardless of shape.
# `_dewrap_citation_shapes` collapses a wrap inside one of these three shapes directly,
# off the identical regexes `_residue_cause` uses, never gated on `inverse`. Each shape
# gets one RED-before/GREEN-after positive test (the wrap alone must not block class 2)
# and one negative-control test (a wrap AND a genuine content change together must still
# fall through to `classified-by-none` -- collapsing wrap markup must never paper over a
# real difference inside or beside the citation).
# ---------------------------------------------------------------------------------------

_EMPTY_REDIRECTS_CSV: Final = "old_id,new_id,old_path,new_path,citing_dir\n"


def _write_pair(
    old_root: pathlib.Path,
    new_root: pathlib.Path,
    rel: pathlib.Path,
    old_text: str,
    new_text: str,
) -> None:
    (old_root / rel.parent).mkdir(parents=True, exist_ok=True)
    (new_root / rel.parent).mkdir(parents=True, exist_ok=True)
    (old_root / rel).write_text(old_text, encoding="utf-8")
    (new_root / rel).write_text(new_text, encoding="utf-8")
    redirects = new_root / "docs" / "REDIRECTS.csv"
    redirects.parent.mkdir(parents=True, exist_ok=True)
    redirects.write_text(_EMPTY_REDIRECTS_CSV, encoding="utf-8")


def test_range_citation_wrap_is_class2(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """A legacy range citation (`FR-PLAT-1..4`, cause2a's own shape) that
    `_reflow_long_lines` wrapped mid-token, with no other change, must classify class 2 --
    the citation is never rewritten by the migration (no `REDIRECTS.csv` row), so
    `inverse` is empty and only `_dewrap_citation_shapes` can reach this wrap.
    """
    old_root = tmp_path / "old"
    new_root = tmp_path / "new"
    rel = pathlib.Path("scripts") / "example_range.py"
    _write_pair(
        old_root,
        new_root,
        rel,
        "# see FR-PLAT-1..4 for background\nX = 1\n",
        "# see FR-PLAT-1..\n# 4 for background\nX = 1\n",
    )
    _init_git(old_root)

    classification = doc_id_cli.classify_migration_diff(old_root, new_root)

    rel_posix = rel.as_posix()
    assert rel_posix in classification.per_class["2-reference-token"], (
        classification.summary()
    )
    assert rel_posix not in classification.per_class[doc_id_cli.CLASSIFIED_BY_NONE]


def test_range_citation_wrap_with_real_change_stays_none(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Negative control: the same wrap, but the range's own upper bound genuinely
    changed (`..4` -> `..5`). Collapsing the wrap must not paper over that -- the retry
    still fails and the hunk still falls through to `classified-by-none`.
    """
    old_root = tmp_path / "old"
    new_root = tmp_path / "new"
    rel = pathlib.Path("scripts") / "example_range_changed.py"
    _write_pair(
        old_root,
        new_root,
        rel,
        "# see FR-PLAT-1..4 for background\nX = 1\n",
        "# see FR-PLAT-1..\n# 5 for background\nX = 1\n",
    )
    _init_git(old_root)

    classification = doc_id_cli.classify_migration_diff(old_root, new_root)

    rel_posix = rel.as_posix()
    assert rel_posix in classification.per_class[doc_id_cli.CLASSIFIED_BY_NONE], (
        classification.summary()
    )
    assert rel_posix not in classification.per_class["2-reference-token"]


def test_slash_compound_chain_wrap_is_class2(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """A 3-id slash-compound chain (`FR-RATE-56/57/58`, the slash-compound cause's own
    shape) wrapped mid-token, with no other change, must classify class 2 -- no single
    `REDIRECTS.csv` row covers a 3+-id chain, so `inverse` cannot reach this wrap either.
    """
    old_root = tmp_path / "old"
    new_root = tmp_path / "new"
    rel = pathlib.Path("scripts") / "example_chain.py"
    _write_pair(
        old_root,
        new_root,
        rel,
        "# see FR-RATE-56/57/58 for background\nX = 1\n",
        "# see FR-RATE-56/\n# 57/58 for background\nX = 1\n",
    )
    _init_git(old_root)

    classification = doc_id_cli.classify_migration_diff(old_root, new_root)

    rel_posix = rel.as_posix()
    assert rel_posix in classification.per_class["2-reference-token"], (
        classification.summary()
    )
    assert rel_posix not in classification.per_class[doc_id_cli.CLASSIFIED_BY_NONE]


def test_slash_compound_chain_wrap_with_real_change_stays_none(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Negative control: the same wrap, but the chain's last id genuinely changed
    (`/58` -> `/59`). The retry still fails and the hunk still falls through to
    `classified-by-none`.
    """
    old_root = tmp_path / "old"
    new_root = tmp_path / "new"
    rel = pathlib.Path("scripts") / "example_chain_changed.py"
    _write_pair(
        old_root,
        new_root,
        rel,
        "# see FR-RATE-56/57/58 for background\nX = 1\n",
        "# see FR-RATE-56/\n# 57/59 for background\nX = 1\n",
    )
    _init_git(old_root)

    classification = doc_id_cli.classify_migration_diff(old_root, new_root)

    rel_posix = rel.as_posix()
    assert rel_posix in classification.per_class[doc_id_cli.CLASSIFIED_BY_NONE], (
        classification.summary()
    )
    assert rel_posix not in classification.per_class["2-reference-token"]


def test_legacy_path_citation_wrap_is_class2(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """A prose citation by its pre-migration literal path (`docs/notes/...`, cause3's own
    shape) wrapped mid-token, with no other change, must classify class 2 -- `inverse` is
    built only from `REDIRECTS.csv`'s id columns, never a citation's own literal path
    string, so it never carries a key for this wrap either.
    """
    old_root = tmp_path / "old"
    new_root = tmp_path / "new"
    rel = pathlib.Path("scripts") / "example_legacypath.py"
    _write_pair(
        old_root,
        new_root,
        rel,
        "# see docs/notes/0010-example.md for background\nX = 1\n",
        "# see docs/\n# notes/0010-example.md for background\nX = 1\n",
    )
    _init_git(old_root)

    classification = doc_id_cli.classify_migration_diff(old_root, new_root)

    rel_posix = rel.as_posix()
    assert rel_posix in classification.per_class["2-reference-token"], (
        classification.summary()
    )
    assert rel_posix not in classification.per_class[doc_id_cli.CLASSIFIED_BY_NONE]


def test_legacy_path_citation_wrap_with_real_change_stays_none(
    doc_id_cli: types.ModuleType, tmp_path: pathlib.Path
) -> None:
    """Negative control: the same wrap, but the cited note's own filename genuinely
    changed (`0010-example.md` -> `0011-example.md`). The retry still fails and the hunk
    still falls through to `classified-by-none`.
    """
    old_root = tmp_path / "old"
    new_root = tmp_path / "new"
    rel = pathlib.Path("scripts") / "example_legacypath_changed.py"
    _write_pair(
        old_root,
        new_root,
        rel,
        "# see docs/notes/0010-example.md for background\nX = 1\n",
        "# see docs/\n# notes/0011-example.md for background\nX = 1\n",
    )
    _init_git(old_root)

    classification = doc_id_cli.classify_migration_diff(old_root, new_root)

    rel_posix = rel.as_posix()
    assert rel_posix in classification.per_class[doc_id_cli.CLASSIFIED_BY_NONE], (
        classification.summary()
    )
    assert rel_posix not in classification.per_class["2-reference-token"]
