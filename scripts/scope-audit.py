#!/usr/bin/env python3
"""Derive a workstream's expected scope from the specs, then look for evidence.

`CLAUDE.md` §13 step 1. The order is the whole point: **enumerate what the specification
requires, then search for evidence of each item.** Auditing the other way round — starting
from what was built and checking it works — can only ever confirm what was built, and is
silent about everything the workstream was supposed to cover and did not.

Both inputs are documents. Requirements come from `docs/specs/`, evidence comes from
`@pytest.mark.req` markers in the test suite. Neither is a recollection of what was
written, which is what makes the result independent of whoever runs it.

    scripts/scope-audit.py PLAT                    # every PLAT requirement, by section
    scripts/scope-audit.py PLAT --sections 3.1,3.2,3.3,3.7,3.8 --extra FR-PLAT-47,FR-PLAT-48

`--sections` restricts to the spec sections a workstream's named areas cover; `--extra`
adds individual requirements it also owns. The resulting count is the number to reconcile
against the roadmap's claim — **a disagreement is itself a finding**, and was one for W2.

Exit code is 1 when any in-scope requirement has no evidence, so a closure procedure can
run this and stop.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
import tomllib
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPECS = ROOT / "docs" / "specs"

_REQUIREMENT = re.compile(r"^\| \*\*((?:FR|NFR)-([A-Z]+)-\d+)\*\*")
_SECTION = re.compile(r"^### (\d+\.\d+) (.+)")
_NFR_HEADING = re.compile(r"^## \d+\. Non-functional requirements")
_MARKER = re.compile(r'@pytest\.mark\.req\("([^"]+)"\)')


def requirements_by_section(module: str) -> dict[str, list[str]]:
    """Every requirement for a module, grouped by the spec section that defines it."""
    found: dict[str, list[str]] = defaultdict(list)
    for spec in sorted(SPECS.glob("*.md")):
        section = "(preamble)"
        for line in spec.read_text(encoding="utf-8").splitlines():
            heading = _SECTION.match(line)
            if heading:
                section = f"{heading.group(1)} {heading.group(2)}"
            elif _NFR_HEADING.match(line):
                section = "NFR"
            match = _REQUIREMENT.match(line)
            if match and match.group(2) == module:
                found[section].append(match.group(1))
    return dict(found)


def _test_roots() -> list[pathlib.Path]:
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return [ROOT / p for p in config["tool"]["pytest"]["ini_options"]["testpaths"]]


def evidence() -> dict[str, list[str]]:
    """Requirement id to the test files claiming it."""
    claimed: dict[str, list[str]] = defaultdict(list)
    for root in _test_roots():
        if not root.is_dir():
            continue
        for test in sorted(root.rglob("test_*.py")):
            for rid in _MARKER.findall(test.read_text(encoding="utf-8")):
                claimed[rid].append(str(test.relative_to(ROOT)))
    return dict(claimed)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("module", help="Module code, e.g. PLAT, DATA, MODEL")
    parser.add_argument(
        "--sections",
        help="Comma-separated section numbers to treat as in scope, e.g. 3.1,3.2",
    )
    parser.add_argument(
        "--extra", help="Comma-separated requirement ids also in scope, e.g. FR-PLAT-47"
    )
    args = parser.parse_args()

    by_section = requirements_by_section(args.module)
    if not by_section:
        print(f"  no requirements found for module {args.module!r}")
        return 1

    wanted = (
        {s.strip() for s in args.sections.split(",")} if args.sections else None
    )
    extra = {r.strip() for r in args.extra.split(",")} if args.extra else set()
    claimed = evidence()

    in_scope: list[str] = []
    print(f"  {args.module} requirements by spec section\n")
    for section in sorted(by_section):
        ids = by_section[section]
        number = section.split(" ")[0]
        selected = wanted is None or number in wanted
        covered = [r for r in ids if r in claimed]
        mark = "IN SCOPE " if selected else "         "
        print(
            f"  {mark} {section:<34} {len(covered):>2}/{len(ids):<2} evidenced"
            + ("" if selected else "   (not in this workstream)")
        )
        if selected:
            in_scope.extend(ids)

    for rid in sorted(extra):
        if rid not in in_scope:
            in_scope.append(rid)
            state = "evidenced" if rid in claimed else "NO EVIDENCE"
            print(f"  IN SCOPE  {rid:<34} {state}")

    missing = [r for r in in_scope if r not in claimed]
    print()
    print(f"  in scope        : {len(in_scope)}")
    print(f"  with evidence   : {len(in_scope) - len(missing)}", end="")
    if in_scope:
        print(f"  ({(len(in_scope) - len(missing)) / len(in_scope):.0%})")
    else:
        print()

    if missing:
        print(f"\n  NO EVIDENCE for {len(missing)}:")
        for rid in missing:
            print(f"      {rid}")
        print(
            "\n  Each needs a verdict before closure: delivered but untested, deferred with\n"
            "  an owner, reassigned to another workstream, or not started. Silence is not\n"
            "  one of the options (CLAUDE.md §13 rule 5)."
        )
        return 1

    print("\n  every in-scope requirement has test evidence")
    return 0


if __name__ == "__main__":
    sys.exit(main())
