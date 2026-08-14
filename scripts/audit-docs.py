#!/usr/bin/env python3
"""Consistency audit for the docs/ specification suite.

Checks (all non-destructive, exit 1 on any failure):
  1. No broken relative markdown links.
  2. Every referenced FR-/NFR- id is defined exactly once in a spec.
  3. No gaps in requirement numbering within a module.
  4. Every spec open question is mirrored in open-questions.md, and vice versa.
  5. Every referenced ADR file exists.
  6. Every spec has the ten sections required by CLAUDE.md §5.
  7. Every JSON Schema parses and has no duplicate keys.

Usage: python3 scripts/audit-docs.py
"""
from __future__ import annotations

import collections
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent / "docs"
REQUIRED_SECTIONS = [
    "Purpose & scope", "Concepts & glossary", "Functional requirements",
    "Data contracts", "Interfaces", "Workflows", "Cross-module dependencies",
    "Tech dependencies", "Non-functional requirements", "Open questions",
]

failures: list[str] = []
notes: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)


def main() -> int:
    md = sorted(ROOT.rglob("*.md"))
    specs = sorted(ROOT.glob("specs/*.md"))

    # 1. relative links
    for f in md:
        for m in re.finditer(r"\[[^\]]*\]\(([^)#\s]+)(#[^)]*)?\)", f.read_text()):
            target = m.group(1)
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            if not (f.parent / target).resolve().exists():
                fail(f"broken link in {f.relative_to(ROOT)}: {target}")

    # 2/3. requirement ids
    defined: dict[str, list[str]] = collections.defaultdict(list)
    for f in specs:
        for m in re.finditer(r"\*\*((?:FR|NFR)-[A-Z]+-\d+)\*\*", f.read_text()):
            defined[m.group(1)].append(f.name)
    for rid, where in defined.items():
        if len(where) > 1:
            fail(f"{rid} defined in multiple specs: {where}")

    referenced: dict[str, set[str]] = collections.defaultdict(set)
    for f in md:
        for m in re.finditer(r"\b((?:FR|NFR)-[A-Z]+-\d+)\b", f.read_text()):
            referenced[m.group(1)].add(str(f.relative_to(ROOT)))
    for rid in sorted(set(referenced) - set(defined)):
        fail(f"{rid} referenced but never defined (in {sorted(referenced[rid])})")

    by_prefix: dict[str, list[int]] = collections.defaultdict(list)
    for rid in defined:
        prefix, num = rid.rsplit("-", 1)
        by_prefix[prefix].append(int(num))
    for prefix, nums in sorted(by_prefix.items()):
        missing = sorted(set(range(1, max(nums) + 1)) - set(nums))
        if missing:
            fail(f"{prefix} has numbering gaps: {missing}")

    notes.append(f"{len(defined)} requirements defined across {len(specs)} specs")

    # 4. open questions
    in_specs = set()
    for f in specs:
        in_specs |= set(re.findall(r"\*\*(OQ-[A-Z]+-\d+)\*\*", f.read_text()))
    oq_file = ROOT / "open-questions.md"
    in_file = set(re.findall(r"\*\*(OQ-[A-Z]+-\d+)\*\*", oq_file.read_text()))
    for q in sorted(in_specs - in_file):
        fail(f"{q} raised in a spec but not mirrored into open-questions.md")
    for q in sorted(in_file - in_specs):
        fail(f"{q} listed in open-questions.md but raised in no spec")
    notes.append(f"{len(in_file)} open questions, all mirrored")

    # 5. ADRs
    adrs = {p.name.split("-")[0] for p in ROOT.glob("adr/0*.md")}
    corpus = "\n".join(f.read_text() for f in md)
    for ref in sorted(set(re.findall(r"ADR-(\d{4})", corpus)) - adrs):
        fail(f"ADR-{ref} referenced but no file exists")

    # 6. spec sections
    for f in specs:
        heads = re.findall(r"^## \d+\.?\s*(?:—\s*)?(.+)$", f.read_text(), re.M)
        lowered = [h.lower() for h in heads]
        for name in REQUIRED_SECTIONS:
            key = name.lower().split("(")[0].strip()
            if not any(key in h for h in lowered):
                fail(f"{f.name} missing required section: {name}")

    # 7. JSON schemas
    def no_dupes(pairs):
        seen = collections.Counter(k for k, _ in pairs)
        dupes = [k for k, c in seen.items() if c > 1]
        if dupes:
            raise ValueError(f"duplicate keys {dupes}")
        return dict(pairs)

    schemas = sorted((ROOT / "contracts").rglob("*.json"))
    for f in schemas:
        try:
            json.load(f.open(), object_pairs_hook=no_dupes)
        except ValueError as exc:
            fail(f"{f.relative_to(ROOT)}: {exc}")
    notes.append(f"{len(schemas)} JSON schemas parsed")

    for note in notes:
        print(f"  {note}")
    if failures:
        print(f"\nFAILED ({len(failures)}):")
        for msg in failures:
            print(f"  - {msg}")
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
