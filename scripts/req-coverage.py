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
import tomllib

ROOT = pathlib.Path(__file__).resolve().parent.parent

#: A requirement id defined in a spec, in either form: `**FR-154**` before the RFC-937
#: id migration, `**FR-1187**` after it (RFC-937 D2). Both are accepted here rather than
#: selected by tree, because this script's other input -- `@pytest.mark.req("...")` markers
#: across ~1 988 sites -- is rewritten by the same migration commit and a marker in the old
#: form on a migrated tree must still be reported as unknown, not silently unparsed.
_REQ_DEFINED = re.compile(r"\*\*((?:FR|NFR)-(?:[A-Z]+-)?\d+)\*\*")


def _test_roots() -> list[pathlib.Path]:
    """The directories pytest collects from, read from pyproject rather than hardcoded.

    This was `packages/` alone until WK-658 added `backend/`. A second code root did not make
    the script fail — it made it silently under-report, and quietly stopped applying the
    "claims a requirement that does not exist" check to every test in the new component.
    Sourcing the list from pytest's own `testpaths` means a new component is covered by
    adding it in one place, which is the place that already has to change.
    """
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    testpaths = config["tool"]["pytest"]["ini_options"]["testpaths"]
    roots = [ROOT / p for p in testpaths]
    missing = [str(r) for r in roots if not r.is_dir()]
    if missing:
        raise SystemExit(f"testpaths names directories that do not exist: {missing}")
    return roots


def main() -> int:
    specified: set[str] = set()
    for spec in sorted((ROOT / "docs" / "specs").glob("*.md")):
        body = spec.read_text(encoding="utf-8")
        specified |= set(_REQ_DEFINED.findall(body))

    claimed: dict[str, list[str]] = {}
    for root in _test_roots():
        for test in sorted(root.rglob("test_*.py")):
            source = test.read_text(encoding="utf-8")
            for rid in re.findall(r'@pytest\.mark\.req\("([^"]+)"\)', source):
                claimed.setdefault(rid, []).append(str(test.relative_to(ROOT)))

    unknown = sorted(set(claimed) - specified)
    print(f"  requirements specified : {len(specified)}")
    if not specified:
        # Zero specified requirements is never a real tree state: `docs/specs/` is eight
        # files of numbered clauses. It means this script's id pattern stopped matching the
        # corpus -- which is what happened at the RFC-937 migration, where the module-scoped
        # pattern above met `**FR-1187**` and matched nothing. Say so; do not divide by it.
        print(
            "\n  FAIL: no requirement ids parsed from docs/specs/ -- the id pattern does "
            "not match this tree's requirement form, so every coverage figure below would "
            "be measured against an empty denominator"
        )
        return 1
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
