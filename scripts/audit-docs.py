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
  8. Every JSON Schema $ref resolves, including cross-file pointers into $defs.
  9. Cross-spec section references ("01 §4.5") point at sections that exist.
 10. No error code is claimed as owned by more than one module.
 11. Module dependency direction respects DEP-1 (no consuming from the right).
 12. Money fields (*_minor) are never written as fractional numbers.
 13. Terms are not redefined in a module glossary after 00-overview defines them.
 14. Every module is exercised by at least one workflow, above a coverage floor.

Usage: python3 scripts/audit-docs.py
"""
from __future__ import annotations

import collections
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent / "docs"
_ABS_PREFIX = "https://contracts.gi-pricing.dev/"
REQUIRED_SECTIONS = [
    "Purpose & scope", "Concepts & glossary", "Functional requirements",
    "Data contracts", "Interfaces", "Workflows", "Cross-module dependencies",
    "Tech dependencies", "Non-functional requirements", "Open questions",
]

failures: list[str] = []
notes: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)



def check_open_question_columns() -> None:
    """15. Every OQ row has an owner and a status drawn from a known set.

    Added after an edit wrote "decided" into the *owner* column and left the status as
    "open": the register then disagreed with the spec about whether a question was settled,
    and all fourteen existing checks passed. A malformed row here is not a typo — this file
    is the project's record of what has been decided.
    """
    allowed = {"open", "decided", "deferred", "superseded"}
    path = ROOT / "open-questions.md"
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = re.match(r"\| (?:~~)?\*\*(OQ-[A-Z]+-\d+)\*\*", line)
        if not match:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            fail(f"open-questions.md:{number}: {match.group(1)} has too few columns")
            continue
        owner = cells[-2].replace("*", "").strip().lower()
        status = cells[-1].replace("*", "").replace("~", "").strip().lower()
        first = status.split()[0] if status else ""
        if first not in allowed:
            fail(
                f"open-questions.md:{number}: {match.group(1)} status {cells[-1]!r} is not "
                f"one of {sorted(allowed)}"
            )
        if not owner or owner in allowed:
            fail(
                f"open-questions.md:{number}: {match.group(1)} owner {cells[-2]!r} looks "
                "like a status — the columns may be shifted"
            )


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
    def no_dupes(pairs: list[tuple[str, object]]) -> dict[str, object]:
        seen = collections.Counter(k for k, _ in pairs)
        dupes = [k for k, c in seen.items() if c > 1]
        if dupes:
            raise ValueError(f"duplicate keys {dupes}")
        return dict(pairs)

    schema_root = ROOT / "contracts" / "schemas"
    schemas = sorted((ROOT / "contracts").rglob("*.json"))
    loaded: dict[pathlib.Path, object] = {}
    for f in schemas:
        try:
            loaded[f] = json.load(f.open(), object_pairs_hook=no_dupes)
        except ValueError as exc:
            fail(f"{f.relative_to(ROOT)}: {exc}")

    # 8. $ref resolution

    def resolve_pointer(doc: object, fragment: str) -> bool:
        """Resolve a JSON Pointer fragment such as '/$defs/QuoteContext'."""
        cur = doc
        for part in fragment.lstrip("/").split("/"):
            part = part.replace("~1", "/").replace("~0", "~")
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return False
        return True

    def check_ref(ref: str, src: pathlib.Path) -> None:
        if ref.startswith(_ABS_PREFIX):
            tail = ref[len(_ABS_PREFIX):]
        elif ref.startswith("#"):
            if len(ref) > 1 and not resolve_pointer(loaded[src], ref[1:]):
                fail(f"{src.relative_to(ROOT)}: local $ref {ref} does not resolve")
            return
        elif ref.startswith(("http://", "https://")):
            return  # external, not our concern
        else:
            tail = ref
        target, _, fragment = tail.partition("#")
        path = (schema_root / target) if ref.startswith(_ABS_PREFIX) else (src.parent / target)
        path = path.resolve()
        if path not in loaded:
            fail(f"{src.relative_to(ROOT)}: $ref {ref} -> missing {target}")
        elif fragment and not resolve_pointer(loaded[path], fragment):
            fail(f"{src.relative_to(ROOT)}: $ref {ref} -> fragment does not resolve")

    def walk(node: object, src: pathlib.Path) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "$ref" and isinstance(value, str):
                    check_ref(value, src)
                else:
                    walk(value, src)
        elif isinstance(node, list):
            for item in node:
                walk(item, src)

    loaded = {f.resolve(): doc for f, doc in loaded.items()}
    for f in schemas:
        if f.resolve() in loaded:
            walk(loaded[f.resolve()], f.resolve())
    notes.append(f"{len(loaded)} JSON schemas parsed, $refs checked")

    # ------------------------------------------------------------------ 9-14
    spec_by_code = {
        "00": "00-overview.md", "01": "01-data-management.md",
        "02": "02-modelling.md", "03": "03-rating-engine.md",
        "04": "04-optimisation.md", "05": "05-monitoring.md",
        "06": "06-governance.md", "07": "07-platform.md",
    }
    spec_text = {f.name: f.read_text() for f in specs}

    # 9. cross-spec section references, e.g. `01` §4.5  /  02 §3.2
    # `(?<![0-9-])` matters: without it the `02` inside a date like `2026-08-15` matches,
    # and any § reference within the next 24 characters is reported as a broken
    # cross-reference to `02`. It reads exactly like a real finding, which is the worst
    # kind of false positive.
    sec_re = re.compile(r"(?<![0-9-])`?(0[0-7])`?[^\n]{0,24}?§(\d+(?:\.\d+)*)")
    for f in md:
        for m in sec_re.finditer(f.read_text()):
            code, sec = m.group(1), m.group(2)
            target = spec_by_code[code]
            body = spec_text.get(target, "")
            top = sec.split(".")[0]
            # a heading "## N." must exist; sub-sections may be "### N.M"
            if not re.search(rf"^#{{2,4}} {re.escape(sec)}[.\s]", body, re.M) and \
               not re.search(rf"^#{{2,4}} {re.escape(top)}\.", body, re.M):
                fail(
                    f"{f.relative_to(ROOT)}: reference to {code} §{sec} — "
                    f"no such section in {target}"
                )

    # 10. error-code ownership is exclusive
    owner: dict[str, str] = {}
    code_re = re.compile(r"\*\*Error codes owned by this module:\*\*(.+?)(?:\n\n|###)", re.S)
    for f in specs:
        m = code_re.search(f.read_text())
        if not m:
            continue
        block = m.group(1)
        for cm in re.finditer(r"`([A-Z][A-Z0-9_]{3,})`(\s*\(re-raised from[^)]*\))?", block):
            code, reraised = cm.group(1), bool(cm.group(2))
            if reraised:
                continue  # explicitly borrowed from the owning module
            if code in owner and owner[code] != f.name:
                fail(
                    f"error code {code} claimed by both {owner[code]} and "
                    f"{f.name} — annotate one as '(re-raised from `NN`)' or "
                    "give ownership to one module"
                )
            owner.setdefault(code, f.name)
    notes.append(f"{len(owner)} error codes, ownership exclusive")

    # 11. DEP-1 build order: a module must not consume from a module to its right
    order = ["PLAT", "GOV", "DATA", "MODEL", "RATE", "OPT", "MON"]
    code_of = {"01": "DATA", "02": "MODEL", "03": "RATE", "04": "OPT",
               "05": "MON", "06": "GOV", "07": "PLAT"}
    for f in specs:
        code = f.name[:2]
        if code not in code_of:
            continue
        me = code_of[code]
        body = f.read_text()
        m = re.search(r"### 7\.1 (?:This module )?[Cc]onsumes(.*?)### 7\.2", body, re.S)
        if not m:
            continue
        for row in m.group(1).splitlines():
            if not row.startswith("| `"):
                continue
            src = re.match(r"\| `(\d\d)", row)
            if not src or src.group(1) not in code_of:
                continue
            other = code_of[src.group(1)]
            if order.index(other) <= order.index(me):
                continue
            # DEP-1a: GOV's audit sink and permission check are cross-cutting interfaces
            if other == "GOV" and re.search(r"audit|permission|authoris|authoriz|RBAC", row, re.I):
                continue
            fail(
                f"{f.name}: DEP-1 violation — {me} consumes from {other}, "
                "which is to its right"
            )

    # 12. money discipline: *_minor fields must never be fractional
    money_re = re.compile(r'"(\w*_minor)"\s*:\s*(-?\d+\.\d+)')
    for f in list(md) + schemas:
        for m in money_re.finditer(f.read_text()):
            fail(
                f"{f.relative_to(ROOT)}: {m.group(1)} written as fractional "
                f"{m.group(2)} (FR-OVR-7)"
            )

    # 13. glossary terms not redefined downstream
    def terms(body: str, section: str) -> set[str]:
        m = re.search(rf"^## {section}\..*?$(.*?)^## ", body, re.S | re.M)
        if not m:
            return set()
        return {t.strip().lower() for t in re.findall(r"^\| \*\*(.+?)\*\* \|", m.group(1), re.M)}
    canon = terms(spec_text["00-overview.md"], "2")
    for f in specs:
        if f.name == "00-overview.md":
            continue
        for t in terms(f.read_text(), "2") & canon:
            fail(
                f"{f.name}: glossary term '{t}' is already defined in "
                "00-overview.md §2 — reference it, do not redefine"
            )

    # 14. workflow coverage per module
    #
    # Most requirements are property-level ("TLS 1.3", "normalise to snake_case") and a
    # workflow legitimately never cites them — journeys cite step-level requirements.
    # So raw orphan count is not a defect signal. What IS a defect is a module no
    # workflow exercises at all, or coverage collapsing for one module while others
    # hold. The floor catches both; it is deliberately low.
    coverage_floor = 0.10
    wf_text = "\n".join(f.read_text() for f in ROOT.glob("workflows/*.md"))
    per_mod: dict[str, list[int]] = collections.defaultdict(lambda: [0, 0])
    for rid in defined:
        if rid.startswith("NFR-"):
            continue
        mod = rid.split("-")[1]
        per_mod[mod][1] += 1
        if rid in wf_text:
            per_mod[mod][0] += 1
    summary = []
    for mod in sorted(per_mod):
        hit, tot = per_mod[mod]
        ratio = hit / tot if tot else 1.0
        summary.append(f"{mod} {ratio:.0%}")
        if ratio < coverage_floor:
            fail(f"workflow coverage for {mod} is {ratio:.0%} ({hit}/{tot}), below the "
                 f"{coverage_floor:.0%} floor — no user journey exercises this module")
    notes.append("workflow coverage: " + ", ".join(summary))

    for note in notes:
        print(f"  {note}")
    # 15. open-question rows have an owner and a recognised status
    check_open_question_columns()

    if failures:
        print(f"\nFAILED ({len(failures)}):")
        for msg in failures:
            print(f"  - {msg}")
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())