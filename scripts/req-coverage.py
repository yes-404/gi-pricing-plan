#!/usr/bin/env python3
"""Report which requirements the test suite claims to satisfy.

`skills-map.md` §9.1 (spec-to-implementation conformance): tests are marked with the
requirement they satisfy, and this turns those marks into a coverage report. The gap
between "specified" and "tested" widens silently otherwise.

This is informational in Phase 1a — almost nothing is implemented yet, so a coverage
threshold would fail every build and teach everyone to ignore it. It gains a floor when
the phase's requirements are meant to be complete.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main() -> int:
    specified: set[str] = set()
    for spec in sorted((ROOT / "docs" / "specs").glob("*.md")):
        specified |= set(re.findall(r"\*\*((?:FR|NFR)-[A-Z]+-\d+)\*\*", spec.read_text()))

    claimed: dict[str, list[str]] = {}
    for test in sorted((ROOT / "packages").rglob("test_*.py")):
        for rid in re.findall(r'@pytest\.mark\.req\("([^"]+)"\)', test.read_text()):
            claimed.setdefault(rid, []).append(str(test.relative_to(ROOT)))

    unknown = sorted(set(claimed) - specified)
    print(f"  requirements specified : {len(specified)}")
    print(f"  requirements marked    : {len(claimed)}  ({len(claimed) / len(specified):.1%})")
    for rid in sorted(claimed):
        print(f"      {rid:16s} {len(claimed[rid])} test file(s)")

    if unknown:
        # A test claiming a requirement that does not exist is a real defect: either a
        # typo, or a requirement that was renumbered in violation of the append-only rule.
        print("\n  FAIL: tests claim requirements that do not exist:")
        for rid in unknown:
            print(f"      {rid}  <- {', '.join(claimed[rid])}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
