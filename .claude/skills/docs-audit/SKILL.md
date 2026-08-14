---
name: docs-audit
description: Verify the integrity of the docs/ specification suite before committing or opening a PR in this GI pricing platform repo. Runs fourteen checks — requirement IDs, cross-references, open-question mirroring, ADRs, spec sections, JSON Schemas, plus structural checks for section references, error-code ownership, dependency direction, money discipline, glossary single-sourcing and workflow coverage — and the decision-gate invariant the script does not cover. Use before any docs commit, after applying research findings, or when asked whether the documentation is consistent or hangs together.
---

# Auditing the docs suite

One command covers most of it:

```bash
python3 scripts/audit-docs.py
```

It exits non-zero and lists failures. Passing output looks like:

```
  408 requirements defined across 8 specs
  45 open questions, all mirrored
  31 JSON schemas parsed, $refs checked

All checks passed.
```

### Bookkeeping (checks 1–8)

No broken relative links; every referenced `FR-`/`NFR-` ID defined exactly once; no
numbering gaps; open questions mirrored in **both** directions; every referenced ADR
exists; all ten required sections present in every spec; every JSON Schema parses with no
duplicate keys; every `$ref` resolves including cross-file `$defs` pointers.

### Structural (checks 9–14)

Bookkeeping passing is not the same as the suite hanging together. These check that it
does:

| # | Check | The defect it catches |
|---|---|---|
| 9 | Cross-spec section references (`` `01` §4.5 ``) resolve | A section is renumbered and every pointer to it silently rots |
| 10 | No error code owned by two modules | Two specs define the same code differently; annotate `` (re-raised from `NN`) `` for deliberate borrowing |
| 11 | Dependencies respect DEP-1 / DEP-1a | A spec's §7.1 lists a module to its right, inverting the build order |
| 12 | `*_minor` fields are never fractional | A money example written as `361.20` violates FR-OVR-7 |
| 13 | No module glossary redefines a `00-overview.md` term | Two definitions drift apart — the exact failure the single-glossary rule prevents |
| 14 | Every module is exercised by a workflow, above a floor | A module no user journey reaches |

**On check 14:** raw orphan count is *not* a defect signal. Most requirements are
property-level ("TLS 1.3", "normalise to snake_case") and a journey legitimately never
cites them. The floor is deliberately low — it catches a module with no journey at all, not
a module with unglamorous requirements.

## The check the script does not do

The roadmap's decision-gate table must cover all 45 open questions **exactly once**. Rows
use the compact range form `OQ-GOV-1..5`:

```bash
python3 - <<'PY'
import re, pathlib, collections
all_oq = set(re.findall(r'\*\*(OQ-[A-Z]+-\d+)\*\*', pathlib.Path('docs/open-questions.md').read_text()))
gate = pathlib.Path('docs/roadmap.md').read_text().split('## 10. Decision gates')[1].split('## 11.')[0]
c = collections.Counter()
for row in [l for l in gate.splitlines() if l.startswith('| ') and 'OQ-' in l]:
    for m in re.finditer(r'OQ-([A-Z]+)-(\d+)(?:\.\.(\d+))?', row):
        mod, a, b = m.group(1), int(m.group(2)), m.group(3)
        for n in range(a, (int(b) if b else a)+1): c[f"OQ-{mod}-{n}"] += 1
print("missing   :", sorted(all_oq - set(c)) or "none")
print("extra     :", sorted(set(c) - all_oq) or "none")
print("duplicated:", sorted(k for k,v in c.items() if v>1) or "none")
PY
```

All three must print `none`.

## Adding a check

Extend `scripts/audit-docs.py` — it is production code, not a scratch script. **Verify a
new check by feeding it deliberately broken input and confirming it fails**, otherwise a
silently passing no-op check is worse than no check.

## When a check fails

Do not weaken the check to make it pass. Broken links and unmirrored open questions are
real defects; fix the document.

## Verified

2026-08-14 — Run repeatedly through the Track A research application, then extended with
checks 9–14. **All six structural checks were proven against deliberately broken input**
before being trusted: a bogus `§99.9` reference, a duplicated error code, an injected
DEP-1 inversion, a fractional `_minor` value, a redefined glossary term, and a raised
coverage floor — each produced exactly one targeted failure, and the suite passed again on
revert.

On first run the structural checks found **16 real defects**: 11 glossary terms redefined
after `00-overview.md` already owned them (already diverging in wording), 3 inverted module
dependencies, and 2 error codes claimed by two modules. Fixing the third dependency
inversion required amending DEP-1 itself — audit and permission checks are cross-cutting
and cannot be a position in a linear chain, which is now DEP-1a.

The `$ref` check was likewise confirmed non-trivial by pointing a `$ref` at a non-existent
`$defs` fragment.
