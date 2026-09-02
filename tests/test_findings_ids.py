"""Two id invariants over `docs/audit/findings/` and the register — F89 limb 3.

**Why these two and not "no duplicate findings file".** On 2026-09-02 two executors filed
different findings as `F87` within an hour, each having correctly computed the next free id
from `main`, neither able to see the other's unmerged PR. The lead's account was that
nothing would have caught it before the second merge overwrote the first's file.

**Half of that is wrong, and it changes what is worth checking.** Measured with
`git merge-tree` against the two real commits, git reports the file collision itself:

    added in both
      our    100644 4edba56... docs/audit/findings/F87.md
      their  100644 4278a53... docs/audit/findings/F87.md

An add/add conflict blocks the merge; the *file* was never going to be overwritten
silently. **What nothing catches is the register.** Two rows citing one id are inserted at
different offsets, merge cleanly, and `audit-docs.py`'s F-id citation check resolves the id
to its one file and passes — so the register can carry two rows for one finding and say
nothing. That is invariant 2.

Invariant 1 is the other half of the same event: a renumber that moves the file and forgets
the heading. It is not hypothetical — the swap that produced these two ids renamed both
files and rewrote both headings, and a check is what makes "I did both" evidence rather
than recollection.

**Deliberately written over copies, never over `ROOT`.** The checking logic is a pure
function of `(findings_dir, register_text)`, so its broken-input proofs build their inputs
in `tmp_path`. Mutating the real tree to prove a check fires is precisely the defect F88
reports, and a test filed in the same commit should not commit it.
"""

from __future__ import annotations

import collections
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
FINDINGS = ROOT / "docs" / "audit" / "findings"
REGISTER = ROOT / "docs" / "audit" / "register.md"

_FILE_ID = re.compile(r"^F\d+$")
_HEADING_ID = re.compile(r"^#\s+(F\d+)\b")
_CITED_ID = re.compile(r"\((F\d+)\)")


def heading_mismatches(findings_dir: pathlib.Path) -> list[str]:
    """Every findings file whose `# F<n>` heading does not name the file's own id."""
    out = []
    for path in sorted(findings_dir.glob("F*.md")):
        if not _FILE_ID.match(path.stem):
            continue  # README.md and anything else non-id-shaped is not this check's
        first = path.read_text(encoding="utf-8").splitlines()[0]
        match = _HEADING_ID.match(first)
        if match is None or match.group(1) != path.stem:
            out.append(f"{path.name}: heading is {first[:60]!r}")
    return out


def duplicated_register_ids(register_text: str) -> list[str]:
    """Every F-id claimed by more than one register row's Finding-id cell.

    Reads cell 1 only. An id *mentioned* in another row's Decision cell is a cross-
    reference and legitimate — the register is full of them — so a whole-line scan would
    flag ordinary prose. The field this splits on is the one `register-lint.py` treats as
    the row's identity.
    """
    seen: list[str] = []
    for line in register_text.splitlines():
        if not line.startswith("|") or line.count("|") < 2:
            continue
        seen += _CITED_ID.findall(line.split("|")[1])
    counted = collections.Counter(seen)
    return sorted(f"{fid} claimed by {n} rows" for fid, n in counted.items() if n > 1)


def test_every_findings_file_heading_names_its_own_id() -> None:
    """Invariant 1, over the real corpus."""
    assert list(FINDINGS.glob("F*.md")), "no findings files — this would pass vacuously"
    assert heading_mismatches(FINDINGS) == []


def test_no_finding_id_is_claimed_by_two_register_rows() -> None:
    """Invariant 2, over the real corpus — the half git does not cover."""
    text = REGISTER.read_text(encoding="utf-8")
    assert _CITED_ID.search(text), "no ids in the register — this would pass vacuously"
    assert duplicated_register_ids(text) == []


def test_a_renamed_file_whose_heading_was_not_updated_is_named(
    tmp_path: pathlib.Path,
) -> None:
    """Broken input for invariant 1: the exact mistake a renumber makes."""
    (tmp_path / "F88.md").write_text("# F89 — renamed, heading forgotten\n", encoding="utf-8")
    (tmp_path / "F90.md").write_text("# F90 — fine\n", encoding="utf-8")
    out = heading_mismatches(tmp_path)
    assert len(out) == 1
    assert out[0].startswith("F88.md")


def test_a_readme_beside_the_findings_is_not_flagged(tmp_path: pathlib.Path) -> None:
    """`docs/audit/findings/README.md` is not id-shaped and must not be swept in — the
    check is scoped by the filename grammar, not by living in the directory."""
    (tmp_path / "README.md").write_text("# Findings\n", encoding="utf-8")
    (tmp_path / "F90.md").write_text("# F90 — fine\n", encoding="utf-8")
    assert heading_mismatches(tmp_path) == []


def test_two_register_rows_claiming_one_id_are_named() -> None:
    """Broken input for invariant 2: the state a clean merge of two unmerged PRs produces,
    which git permits and `audit-docs.py` passes."""
    text = (
        "| Finding id | Concerns | Work item | Phase | Decision |\n"
        "|---|---|---|---|---|\n"
        "| One thing (F87) | a | — | 2 | carry forward |\n"
        "| A different thing (F87) | b | — | 2 | carry forward |\n"
        "| A third thing (F88) | c | — | 2 | carry forward |\n"
    )
    assert duplicated_register_ids(text) == ["F87 claimed by 2 rows"]


def test_an_id_cross_referenced_in_a_decision_cell_is_not_a_second_claim() -> None:
    """The false positive a whole-line scan would produce. Rows cite each other constantly;
    only the Finding-id cell claims an id."""
    text = (
        "| One thing (F87) | a | — | 2 | carry forward, bundled with (F88) |\n"
        "| Another (F88) | b | — | 2 | see (F87) |\n"
    )
    assert duplicated_register_ids(text) == []


@pytest.mark.parametrize("dropped", ["heading", "register"])
def test_each_invariant_fails_on_its_own_input_and_not_the_other(
    tmp_path: pathlib.Path, dropped: str
) -> None:
    """The two checks are independent: neither masks the other's breakage. Without this a
    single over-broad predicate could satisfy both tests above while covering one case."""
    if dropped == "heading":
        (tmp_path / "F91.md").write_text("# F92 — wrong\n", encoding="utf-8")
        assert heading_mismatches(tmp_path)
        assert duplicated_register_ids("| ok (F91) | a | — | 2 | d |\n") == []
    else:
        (tmp_path / "F91.md").write_text("# F91 — right\n", encoding="utf-8")
        assert heading_mismatches(tmp_path) == []
        assert duplicated_register_ids(
            "| a (F91) | a | — | 2 | d |\n| b (F91) | a | — | 2 | d |\n"
        )
