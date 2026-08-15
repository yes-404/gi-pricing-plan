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
    scripts/scope-audit.py DATA --endpoints        # also check the §5.1 endpoint table
    scripts/scope-audit.py DATA --catalogue VR     # also check a declared catalogue

**A requirement can also summarise a catalogue it does not enumerate.** `01` FR-DATA-16
says "validation covers four layers", which one test can evidence — while §4.4's catalogue
of 38 named rules behind it was 12 implemented. `--catalogue VR` compares the ids a spec
declares against the ids the code names, which is the difference between "the layers work"
and "the rules exist".

**A requirement can be fully evidenced while the module is unreachable.** Requirement
markers live on unit and service tests, so a module can pass every one of them and expose
not a single HTTP route — which is exactly what `--endpoints` found for W4: 49 of 50
`DATA` requirements evidenced, and 0 of the 28 endpoints `01` §5.1 declares. Coverage of
the requirement list is not coverage of the interface.

`--sections` restricts to the spec sections a workstream's named areas cover; `--extra`
adds individual requirements it also owns. The resulting count is the number to reconcile
against the roadmap's claim — **a disagreement is itself a finding**, and was one for W2.

Exit code is 1 when any in-scope requirement has no evidence, so a closure procedure can
run this and stop.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import tomllib
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPECS = ROOT / "docs" / "specs"

_REQUIREMENT = re.compile(r"^\| \*\*((?:FR|NFR)-([A-Z]+)-\d+)\*\*")
# Both heading levels. Specs differ: `07` puts requirements under `### 3.2 Jobs`, while
# `00` puts them under `## 3. Functional requirements`. Matching only `###` made the last
# level-3 heading stick, and every FR-OVR requirement was attributed to
# "2.6 Terms deliberately avoided" — found by running this against a second module, which
# is the reason to do that before trusting a new check.
_SECTION = re.compile(r"^(#{2,3}) (\d+(?:\.\d+)?)\.?\s+(.+)")
_NFR_HEADING = re.compile(r"^#{2,3} \d+(?:\.\d+)?\.?\s+Non-functional requirements")
_MARKER = re.compile(r'@pytest\.mark\.req\("([^"]+)"\)')
# `| \`GET\` | \`/api/v1/datasets\` | ... |` — the §5.1 interface tables. The method cell
# may hold several (`GET`/`PUT`), and paths carry `{placeholders}`.
_ENDPOINT = re.compile(
    r"^\|\s*`?([A-Z]+(?:`?/`?[A-Z]+)*)`?\s*\|\s*`([^`]+)`\s*\|"
)


def requirements_by_section(module: str) -> dict[str, list[str]]:
    """Every requirement for a module, grouped by the spec section that defines it."""
    found: dict[str, list[str]] = defaultdict(list)
    for spec in sorted(SPECS.glob("*.md")):
        section = "(preamble)"
        for line in spec.read_text(encoding="utf-8").splitlines():
            if _NFR_HEADING.match(line):
                section = "NFR"
            elif heading := _SECTION.match(line):
                section = f"{heading.group(2)} {heading.group(3)}"
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


#: `| `VR-STR-1` column-presence | fail | ... |` — a spec's catalogue rows.
_CATALOGUE = re.compile(r"^\| `([A-Z]{2,4}-[A-Z]{2,4}-\d+)` ([a-z0-9-]+)")


def report_catalogue(module: str, prefix: str) -> int:
    """Compare a spec's declared catalogue against the ids the code names.

    Coverage is claimed by a docstring naming the id, as `VR-ACT-1/2/8` does. That is a
    claim rather than a proof, exactly like a `@pytest.mark.req` marker, and it is checked
    the same way: by reading the ones that matter. What it catches reliably is the id
    nothing mentions at all.
    """
    spec = owning_spec(module)
    if spec is None:
        print(f"\n  no spec owns module {module!r}")
        return 0
    text = spec.read_text(encoding="utf-8")
    declared = [
        (rid, name)
        for line in text.splitlines()
        for match in [_CATALOGUE.match(line)]
        if match and (rid := match.group(1)).startswith(f"{prefix}-") and (name := match.group(2))
    ]
    if not declared:
        print(f"\n  {spec.name} declares no {prefix}-* catalogue")
        return 0

    named: set[str] = set()
    for source in sorted((ROOT / "packages").rglob("*.py")) + sorted(
        (ROOT / "backend" / "src").rglob("*.py")
    ):
        for found in re.findall(rf"{prefix}-[A-Z]{{2,4}}-[\d/]+", source.read_text("utf-8")):
            head, _, tail = found.rpartition("-")
            for part in tail.split("/"):
                named.add(f"{head}-{part}")

    by_layer: dict[str, list[tuple[str, str, bool]]] = defaultdict(list)
    for rid, name in declared:
        by_layer[rid.split("-")[1]].append((rid, name, rid in named))

    print(f"\n  {module} catalogue declared in {spec.name}\n")
    missing: list[str] = []
    for layer, rows in sorted(by_layer.items()):
        have = sum(1 for *_, ok in rows if ok)
        print(f"  {layer:<8} {have:>3} / {len(rows):<3} implemented")
        missing.extend(f"{rid} {name}" for rid, name, ok in rows if not ok)

    total = len(declared)
    print(f"  {'TOTAL':<8} {total - len(missing):>3} / {total}")
    if missing:
        print(f"\n  NOT IMPLEMENTED — {len(missing)}:")
        for entry in missing:
            print(f"      {entry}")
        return 1
    return 0


def owning_spec(module: str) -> pathlib.Path | None:
    """The spec that *defines* a module, not merely one that mentions it.

    Almost every spec references `FR-DATA-*` somewhere — cross-module dependencies are the
    point of §7 — so "contains the module code" selects nearly the whole suite and drags
    in `03`'s rating endpoints as if `01` had declared them. Ownership is where the
    requirement rows are.
    """
    counts = {
        spec: len(re.findall(rf"^\| \*\*(?:FR|NFR)-{module}-\d+\*\*", spec.read_text(
            encoding="utf-8"), re.MULTILINE))
        for spec in sorted(SPECS.glob("*.md"))
    }
    best = max(counts, key=lambda spec: counts[spec])
    return best if counts[best] else None


def declared_endpoints(module: str) -> set[tuple[str, str]]:
    """The (method, path) pairs a module's spec declares in its REST API table."""
    declared: set[tuple[str, str]] = set()
    spec = owning_spec(module)
    if spec is not None:
        text = spec.read_text(encoding="utf-8")
        for line in text.splitlines():
            match = _ENDPOINT.match(line)
            if not match:
                continue
            path = match.group(2)
            if not path.startswith("/"):
                continue
            for method in re.split(r"`?/`?", match.group(1)):
                declared.add((method.strip("`"), _normalise_path(path)))
    return declared


def _normalise_path(path: str) -> str:
    """`/datasets/{slug}` and `/datasets/{dataset_slug}` are the same endpoint.

    The parameter's *name* is an implementation choice; only its position is a contract.
    Comparing the names instead would report fourteen missing PLAT endpoints that are all
    published and working — and a check that cries wolf is one everybody learns to skip.
    """
    # A query string in the spec's path cell documents the filters, not a different
    # endpoint: `/jobs?status=` and `/jobs` are one route.
    return re.sub(r"\{[^}]*\}", "{}", path.split("?")[0])


#: Served by FastAPI itself and absent from `paths` by construction — a schema does not
#: list the URL it is served from. Excluding them is not a waiver; they are published, and
#: the alternative is three permanent false alarms that train the reader to skim.
_FRAMEWORK_PATHS = frozenset({"/openapi.json", "/docs", "/redoc"})


def implemented_endpoints() -> set[tuple[str, str]]:
    """The (method, path) pairs the committed OpenAPI contract publishes.

    Read from `docs/contracts/`, not from the running app: the contract is the published
    artifact (FR-PLAT-48), and CI already fails when the app drifts from it. Auditing the
    app instead would make this check pass on a route that was never published.
    """
    contract = ROOT / "docs" / "contracts" / "openapi" / "generated.json"
    if not contract.exists():
        return set()
    document = json.loads(contract.read_text(encoding="utf-8"))
    return set(_FRAMEWORK_PATHS and {("GET", path) for path in _FRAMEWORK_PATHS}) | {
        (method.upper(), _normalise_path(path))
        for path, operations in document.get("paths", {}).items()
        for method in operations
        if method.upper() in {"GET", "POST", "PUT", "PATCH", "DELETE"}
    }


def report_endpoints(module: str) -> int:
    declared = declared_endpoints(module)
    if not declared:
        print(f"\n  {module} declares no REST endpoints")
        return 0
    implemented = implemented_endpoints()
    missing = sorted(declared - implemented)

    print(f"\n  {module} endpoints declared in the spec's §5.1 interface table\n")
    print(f"  declared        : {len(declared)}")
    print(f"  published       : {len(declared) - len(missing)}"
          f"  ({(len(declared) - len(missing)) / len(declared):.0%})")
    if missing:
        print(f"\n  NOT PUBLISHED — {len(missing)}:")
        for method, path in missing:
            print(f"      {method:<6} {path}")
        print(
            "\n  A module whose requirements are all evidenced can still be unreachable.\n"
            "  Each of these needs the same verdict as a missing requirement."
        )
        return 1
    print("\n  every declared endpoint is published in the contract")
    return 0


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
    parser.add_argument(
        "--endpoints",
        action="store_true",
        help="Also check the spec's §5.1 endpoint table against the published contract",
    )
    parser.add_argument(
        "--catalogue",
        metavar="PREFIX",
        help="Also check a declared catalogue by id prefix, e.g. VR for `01` §4.4",
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
    endpoint_gap = report_endpoints(args.module) if args.endpoints else 0
    catalogue_gap = (
        report_catalogue(args.module, args.catalogue) if args.catalogue else 0
    )
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
    return endpoint_gap or catalogue_gap


if __name__ == "__main__":
    sys.exit(main())
