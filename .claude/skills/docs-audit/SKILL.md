---
name: docs-audit
description: Verify the integrity of the docs/ specification suite before committing or opening a PR in this GI pricing platform repo. Runs the requirement-ID, cross-reference, open-question mirroring, ADR, spec-section and JSON Schema checks, plus the decision-gate coverage invariant the script does not cover. Use before any docs commit, after applying research findings, or when asked whether the documentation is consistent.
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

It verifies: no broken relative links; every referenced `FR-`/`NFR-` ID defined exactly
once; no numbering gaps; open questions mirrored in **both** directions; every referenced
ADR exists; all ten required sections present in every spec; every JSON Schema parses with
no duplicate keys; every `$ref` resolves including cross-file `$defs` pointers.

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

2026-08-14 — Run repeatedly through the Track A research application. Confirmed the
`$ref` resolution check is not a no-op by pointing a `$ref` at a non-existent `$defs`
fragment: the script reported three failures and exited 1, then passed again once
reverted. The decision-gate snippet caught a genuine false alarm in an earlier ad-hoc
version of itself that mishandled the `..` range form.
