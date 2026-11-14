"""The one list of frozen paths (ADR-2136), read by `freeze-check.py`, by `audit-docs.py`
(which does not scan a frozen record) and by `tests/test_freeze_check.py`.

Path prefixes end in `/`; anything else is an exact path. Standard library only.
"""
from __future__ import annotations

FROZEN: tuple[str, ...] = (
    "docs/plans/",
    "docs/ledgers/",
    "docs/rulings/",
    "docs/closures/",
    "docs/findings/",
    "docs/rfcs/",
    "docs/research/",
    "docs/roadmap.md",
    "docs/INDEX.md",
    "docs/open-questions.md",
    "docs/REDIRECTS.csv",
    "docs/_templates/",
    "docs/process/residue-ceiling-record.md",
    "docs/process/delivery-process.md",
    "docs/process/delivery-process.core.json",
    "docs/process/document-ids.md",
)


def is_frozen(path: str) -> bool:
    """True when the repo-relative, `/`-separated `path` is under a frozen entry."""
    return any(path == f or (f.endswith("/") and path.startswith(f)) for f in FROZEN)


#: The families the new frame still governs: checks 30, 35 and 36 apply here and nowhere else
#: (skill front matter, generated contracts and every frozen record are out by family).
GOVERNED: tuple[str, ...] = ("docs/specs/", "docs/adrs/", "docs/workflows/", "docs/process/")


def is_governed(path: str) -> bool:
    """True when `path` is in a governed family and not frozen (kept process pages only)."""
    return not is_frozen(path) and path.startswith(GOVERNED)
