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
import ast
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
_ENDPOINT = re.compile(r"^\|\s*`?([A-Z]+(?:`?/`?[A-Z]+)*)`?\s*\|([^|]+)\|")
#: Every backticked token in the path cell. The cell may hold **several** paths —
#: `07` §5.1's health row is ``| `GET` | `/healthz`, `/readyz`, `/version` | …``. Capturing
#: one backticked token matched that row not at all, so three published, working endpoints
#: were audited in neither direction and PLAT's declared count understated its own table by
#: three. A check that silently sees less than the spec says is the failure this script
#: exists to catch, one level up.
_PATH_IN_CELL = re.compile(r"`([^`]+)`")


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


def _ids_in_code(source: pathlib.Path, pattern: str) -> set[str]:
    """Catalogue ids that appear **as data**, not in a comment or a docstring.

    The scan used to be a plain `re.findall` over the file text, which counted every
    mention — and since nothing in this repository stores catalogue ids as data, every
    count came from prose. One docstring reading `VR-ACT-1/2/8` was expanded into three
    "implemented" rules, two of which appear in no source file at all.

    Parsing to an AST drops comments (they never reach it) and docstrings (skipped
    explicitly below), leaving string literals a program actually evaluates. An id in a
    registry counts; an id in a sentence does not.
    """
    try:
        tree = ast.parse(source.read_text(encoding="utf-8"))
    except SyntaxError:
        return set()

    docstrings: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            first = node.body[0] if node.body else None
            if (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            ):
                docstrings.add(id(first.value))

    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) in docstrings:
                continue
            for match in re.findall(pattern, node.value):
                head, _, tail = match.rpartition("-")
                for part in tail.split("/"):
                    found.add(f"{head}-{part}")
    return found


def report_catalogue(module: str, prefix: str) -> int:
    """Compare a spec's declared catalogue against the ids the code carries **as data**.

    `01` §4.4 says "Rule IDs here are stable and referenced by workflows and by the UI",
    which is a claim about data: something must name `VR-ACT-1` for anything to reference
    it. `BUILTIN_ROLES` is what that looks like when it is true.

    Counting mentions instead — the first version of this check — reported 38 of 38 while
    the number of built-in rules the code could name was zero. Every hit was a docstring.
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

    # **Source only.** Scanning tests too would let a rule that exists nowhere but in a
    # test file read as implemented — which is the precise inversion of what this check is
    # for, and it was doing exactly that until a deliberately-broken run failed to notice
    # a deleted rule id.
    named: set[str] = set()
    sources = [
        path
        for root in ((ROOT / "packages"), (ROOT / "backend" / "src"))
        for path in sorted(root.rglob("*.py"))
        if "tests" not in path.parts
    ]
    for source in sources:
        named |= _ids_in_code(source, rf"{prefix}-[A-Z]{{2,4}}-[\d/]+")

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
            paths = [p for p in _PATH_IN_CELL.findall(match.group(2)) if p.startswith("/")]
            for path in paths:
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


#: A token that lost its prefix to a comma split, e.g. the `41` in `FR-RATE-40,41`.
_BARE_NUMBER = re.compile(r"^\d+$")


def _extra_ids(raw: str, known: set[str], module: str) -> set[str] | None:
    """Parse `--extra`'s comma list, refusing any token that names no real requirement.

    The parser is a literal `raw.split(",")` with no shared-prefix inheritance: a comma
    reads to a human as "and repeat the prefix", but the parser reads it as a plain
    separator. `--extra FR-RATE-40,41,42` is not three requirement ids, it is
    `FR-RATE-40`, `"41"` and `"42"`. Before this check existed, `main` folded every token
    straight into scope regardless, and an unmatched one still got a `NO EVIDENCE` row
    printed for it — indistinguishable from a real requirement lacking a test, and with one
    bogus token swapped in for the id it silently replaced, the in-scope *count* still came
    out looking right (`.claude/skills/close-workstream/SKILL.md`, incident of 2026-08-29,
    PR #395). This validates every token against `module`'s own requirement ids — already
    parsed by `requirements_by_section` into `known` — before any of them reaches scope,
    and refuses the whole list rather than silently accepting the good ones and burying the
    bad ones in the report.

    Returns the parsed set, or `None` after printing the diagnostic (the caller returns 1).
    A bare-number token is given a targeted hint — the one shape this has actually failed
    in — naming the prefix it most likely dropped; anything else gets the plain refusal.
    """
    tokens = [token.strip() for token in raw.split(",")]
    bad: list[str] = []
    last_prefix: str | None = None
    for token in tokens:
        if token in known:
            last_prefix = token.rsplit("-", 1)[0]
            continue
        if _BARE_NUMBER.match(token) and last_prefix is not None:
            guess = f"{last_prefix}-{token}"
            bad.append(
                f"      {token!r} — comma-splitting does not repeat the {last_prefix!r} "
                f"prefix from the id before it; did you mean {guess!r}?"
            )
        else:
            bad.append(f"      {token!r} — no {module} requirement has this id")
    if bad:
        print(f"\n  --extra names {len(bad)} token(s) matching no requirement:\n")
        for line in bad:
            print(line)
        print(
            "\n  Write every id out in full — a comma-separated list does not inherit a\n"
            "  shared prefix the way it reads to a human."
        )
        return None
    return set(tokens)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("module", help="Module code, e.g. PLAT, DATA, MODEL")
    parser.add_argument(
        "--sections",
        help="Comma-separated section numbers to treat as in scope, e.g. 3.1,3.2",
    )
    parser.add_argument(
        "--extra",
        help="Comma-separated requirement ids also in scope, each written out in full, "
        "e.g. FR-PLAT-47,FR-PLAT-48 (NOT FR-PLAT-47,48 — the comma does not repeat "
        "the prefix)",
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
    extra: set[str] = set()
    if args.extra:
        known = {rid for ids in by_section.values() for rid in ids}
        parsed = _extra_ids(args.extra, known, args.module)
        if parsed is None:
            return 1
        extra = parsed
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
            "  one of the options (CLAUDE.md §13 rule 1)."
        )
        return 1

    print("\n  every in-scope requirement has test evidence")
    return endpoint_gap or catalogue_gap


if __name__ == "__main__":
    sys.exit(main())
