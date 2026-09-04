"""`scripts/register-owed.py` — NT-0015 P5's owed-list generator, Ruling 52's binding.

Proves, per `CLAUDE.md` §13 ("a check that has never printed a failure has not been
tested"): the script finds a row genuinely owed, omits one that is resolved, and refuses a
dirty or uncommitted revision rather than silently citing one. Also proves the specific
shape F41 names — an owner named only in the Decision column, under a different Work item
column — is found, since a Work-item-only search is the exact mistake this script exists to
not repeat.

No `@pytest.mark.req` marker: correctness of the audit tool itself, not evidence for a
numbered platform requirement (same reasoning `test_register_lint.py` gives).
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
from typing import Any, cast

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "register-owed.py"
REGISTER = ROOT / "docs" / "audit" / "register.md"

_spec = importlib.util.spec_from_file_location("_register_owed_under_test", SCRIPT)
assert _spec is not None
assert _spec.loader is not None
register_owed = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(register_owed)

register_lint = register_owed.register_lint


def _write(tmp_path: pathlib.Path, content: str) -> pathlib.Path:
    f = tmp_path / "register.md"
    f.write_text(content, encoding="utf-8")
    return f


def _parse(tmp_path: pathlib.Path, content: str) -> list[Any]:
    """Returns `register_lint.Row` objects; typed `list[Any]` because `register_lint` is a
    module loaded dynamically by path (a hyphenated filename cannot be imported normally,
    same reason `test_register_lint.py` gives), so mypy cannot resolve its attributes as
    types — the same reason that file's own helper casts rather than annotates precisely.
    """
    rows, problems = register_lint.parse_register(_write(tmp_path, content))
    assert problems == []
    return cast("list[Any]", rows)


_HEADER = "| Finding id | Concerns | Work item | Phase | Decision |\n|---|---|---|---|---|\n"


def _row(finding: str, work: str, phase: str, decision: str) -> str:
    return f"| {finding} | concerns | {work} | {phase} | {decision} |\n"


# --- Finds an owed row --------------------------------------------------------------------

def test_finds_a_row_owned_via_the_work_item_column(tmp_path: pathlib.Path) -> None:
    content = _HEADER + _row(
        "X (F999990)", "W11 Slice 2", "2",
        "carry forward with an owner — the frontend workstream",
    )
    rows = _parse(tmp_path, content)
    matches = register_owed.select_matches(rows, "W11")
    assert [m.row.finding_id for m in matches] == ["X (F999990)"]
    assert matches[0].excluded_resolved is False


def test_finds_a_row_owned_only_via_the_decision_column_not_work_item(
    tmp_path: pathlib.Path,
) -> None:
    """The F41/F-W9-1 shape, reproduced with synthetic ids: the Work item column names the
    slice that *filed* the row (`SL-99991`), and the Decision column names the actual
    *owner* of the carried work (`the WK-99990 scoring workstream`) — a search restricted
    to the Work item column would miss this row exactly as F41's hand-compiled list did
    for the real NFR-RATE-13/14 row.

    Synthetic ids respelled to NT-0019's post-migration shapes (2026-09-04, W37-6
    exec-ids, class-1 fix per the deputy's ruling): `register-owed.py`'s own matching
    (`_word_boundary`/`select_matches`, this module) is form-agnostic — a generic
    word-boundary string search over whatever the Work item and Decision columns hold,
    with no legacy-shape regex anywhere in the script (confirmed by reading it: the only
    two compiled patterns are `_PHASE_ID` and `_word_boundary`'s own generic wrapper, both
    shape-independent) — so nothing in the *script* needed migrating; only these synthetic
    placeholder ids did, because a legacy-shaped example left standing here reads as this
    test's SUBJECT still speaking the pre-migration vocabulary, which it never did.
    """
    content = _HEADER + _row(
        "NFR-991 (FD-99991)", "SL-99991", "2",
        "carry forward with an owner — the WK-99990 scoring workstream; WK-99989's "
        "measurements recorded",
    )
    rows = _parse(tmp_path, content)
    matches = register_owed.select_matches(rows, "WK-99990")
    assert [m.row.finding_id for m in matches] == ["NFR-991 (FD-99991)"]

    # And a Work-item-only search (the mistake this script exists not to repeat) would have
    # missed it — proven directly, not asserted.
    work_item_only = register_owed._word_boundary("WK-99990").search(rows[0].fields[2])
    assert work_item_only is None, "the Work item column alone must not name WK-99990"


def test_word_boundary_does_not_false_positive_on_a_longer_token(
    tmp_path: pathlib.Path,
) -> None:
    """`WK-1` must not match `WK-11`, `WK-10`, or `WK-110` — a naive substring search
    would. Post-migration `WK-` shape (2026-09-04, row (d8), task #30) rather than the
    bare pre-migration `W<n>` this fixture used before: the boundary property under test
    is identical either way, and the bare shape was itself tripping row (d8)'s bare
    work-key check on this file's own fixture data.
    """
    content = _HEADER + _row(
        "X (F999992)", "WK-11", "2",
        "carry forward with an owner — WK-110's own cleanup slice",
    )
    rows = _parse(tmp_path, content)
    assert register_owed.select_matches(rows, "WK-1") == []
    assert len(register_owed.select_matches(rows, "WK-11")) == 1


# --- Omits a resolved row -------------------------------------------------------------------

def test_omits_a_row_that_opens_with_a_resolution_marker(tmp_path: pathlib.Path) -> None:
    content = _HEADER + _row(
        "Y (F999993)", "W11", "2",
        "*resolved 2026-08-28 (PR #302) — the fix landed, nothing further owed.*",
    )
    rows = _parse(tmp_path, content)
    matches = register_owed.select_matches(rows, "W11")
    assert len(matches) == 1
    assert matches[0].excluded_resolved is True
    owed = [m for m in matches if not m.excluded_resolved]
    assert owed == [], "a row opening with a resolution marker must not appear as owed"


def test_a_resolved_row_is_named_in_the_rendered_output_not_silently_dropped(
    tmp_path: pathlib.Path,
) -> None:
    """The F28 shape: a row can open `**Fixed**` and still carry open sub-items in the same
    cell. This script does not try to parse that distinction (P4's job); instead it must
    never let an excluded row vanish with no trace — it is named in a second section so a
    reader can catch a wrongly-excluded row.
    """
    content = _HEADER + _row(
        "Z (F999994)", "W11", "2",
        "**Fixed** — most of it. Still carried: one sub-item, unowned.",
    )
    rows = _parse(tmp_path, content)
    matches = register_owed.select_matches(rows, "W11")
    rendered = register_owed.render(
        "W11", matches, "abc1234 (`main`)", "python3 scripts/register-owed.py W11"
    )
    assert "Z (F999994)" in rendered
    assert "Excluded as opening with a resolution marker" in rendered


# --- Phase and review modes -----------------------------------------------------------------

def test_phase_mode_matches_a_compound_phase_field(tmp_path: pathlib.Path) -> None:
    """A row can span several phases (the register's real F22 shape: `2/3/4`)."""
    content = _HEADER + _row(
        "P (F999995)", "—", "2/3/4", "carry forward — phase boundary",
    )
    rows = _parse(tmp_path, content)
    assert len(register_owed.select_matches(rows, "3")) == 1
    assert register_owed.select_matches(rows, "1b") == []


def test_review_mode_matches_a_row_naming_the_14_review(tmp_path: pathlib.Path) -> None:
    content = _HEADER + _row(
        "R (F999989)", "W11", "2",
        "carry forward — unowned, needs its own authorisation; absent a named event this "
        "decays to the next CLAUDE.md §14 phase review per this register's own header rule",
    )
    rows = _parse(tmp_path, content)
    matches = register_owed.select_matches(rows, "review")
    assert [m.row.finding_id for m in matches] == ["R (F999989)"]


def test_review_mode_does_not_match_a_row_with_no_14_mention(tmp_path: pathlib.Path) -> None:
    content = _HEADER + _row(
        "S (F999988)", "W11", "2", "carry forward with an owner — W14",
    )
    rows = _parse(tmp_path, content)
    assert register_owed.select_matches(rows, "review") == []


# --- Dirty-tree / uncommitted-revision refusal (Ruling 52 constraint 1, enforced) ----------

def _git(repo: pathlib.Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def test_refuses_a_register_with_an_uncommitted_diff(tmp_path: pathlib.Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs" / "audit").mkdir(parents=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "test")
    register = repo / "docs" / "audit" / "register.md"
    register.write_text(_HEADER, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "initial")

    assert register_owed._dirty_path(repo, register) is None, "clean tree must not refuse"

    register.write_text(_HEADER + "extra uncommitted line\n", encoding="utf-8")
    message = register_owed._dirty_path(repo, register)
    assert message is not None, "an uncommitted diff to the register must be refused"
    assert "uncommitted diff" in message


def test_a_clean_committed_register_names_a_resolvable_revision(
    tmp_path: pathlib.Path,
) -> None:
    repo = tmp_path / "repo2"
    (repo / "docs" / "audit").mkdir(parents=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "test")
    register = repo / "docs" / "audit" / "register.md"
    register.write_text(_HEADER, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "initial")

    assert register_owed._dirty_path(repo, register) is None
    revision = register_owed._revision(repo)
    # A short SHA (git's default abbreviation is at least 4 hex chars), never a bare date.
    assert revision, "a clean commit must produce a non-empty, resolvable revision"
    sha_part = revision.split(" ")[0]
    assert len(sha_part) >= 4
    assert all(c in "0123456789abcdef" for c in sha_part)


# --- Live register: control + real-close reconciliation ------------------------------------

def test_live_register_parses_cleanly_for_owed_queries() -> None:
    """Control: without this, every test above could pass while the real register is
    unparseable by this script (Ruling 50 §3's control, applied here).
    """
    rows, problems = register_lint.parse_register(REGISTER)
    assert problems == []
    assert len(rows) > 0


def test_check_29_wiring_is_undisturbed() -> None:
    """This script imports `register-lint.py` by path exactly as its own tests do; importing
    it a second time here must not change what `scripts/audit-docs.py` reports.
    """
    result = subprocess.run(
        ["python3", "scripts/audit-docs.py"], capture_output=True, text=True, cwd=ROOT
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "check 29" in result.stdout
