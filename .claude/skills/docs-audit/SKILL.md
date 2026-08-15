---
name: docs-audit
description: Verify the integrity of the docs/ specification suite and the .claude/notes/ working notes before committing or opening a PR in this GI pricing platform repo. Runs twenty checks — requirement IDs, cross-references, open-question mirroring, ADRs, spec sections, JSON Schemas, plus structural checks for section references, error-code ownership, dependency direction, money discipline, glossary single-sourcing and workflow coverage, plus the notes' header block, numbering, index agreement and references — and the decision-gate invariant the script does not cover. Use before any docs commit, before any working-note commit, after applying research findings, or when asked whether the documentation is consistent or hangs together.
---

# Auditing the docs suite

One command covers most of it:

```bash
python3 scripts/audit-docs.py
```

It exits non-zero and lists failures. Passing output looks like:

```
  418 requirements defined across 8 specs
  46 open questions, all mirrored
  38 JSON schemas parsed, $refs checked
  99 error codes, ownership exclusive
  workflow coverage: DATA 50%, GOV 37%, MODEL 46%, ...
  2 working notes, indexed and numbered

All checks passed.
```

**On Windows**, the script reads every file as UTF-8 explicitly. It did not always: bare
`read_text()` picked up cp1252 and the audit died on the first em-dash in the suite, which
meant the gate could not be run at all on the maintainer's own machine while passing on
CI's Linux runner. If a new check reads a file, pass `encoding="utf-8"`.

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

### The register and the notes (checks 15–20)

| # | Check | The defect it catches |
|---|---|---|
| 15 | Every `OQ-` row has an owner and a recognised status | "decided" written into the *owner* column while the status still says open |
| 16 | Every working note has the header block and a known status | A note with no deliverable or no verdict — the two fields that make it actionable |
| 17 | Note numbering: `NNNN-kebab.md`, unique, matching the `NT-NNNN` heading | A number reused or a heading that disagrees with its filename, so an `NT-0002` reference points at two things |
| 18 | The `.claude/notes/README.md` index and the directory agree, both ways | A note added and never indexed, or an index row outliving its file |
| 19 | Every link, `FR-`/`NFR-`, `OQ-`, `ADR-` and `NT-` reference in a note resolves | A note citing a requirement — or a superseding note — that never existed, which reads exactly like one that does |
| 20 | No note defines a requirement id in the bold `**FR-…**` form | A requirement escaping `docs/specs/`, where `CLAUDE.md` §5's permanence rule does not reach it |

**Checks 16–20 cover the mechanical half of `.claude/notes/README.md`'s audit standard.**
The other half — is this status still *true*, is this deliverable still right for the
current phase — is judgement, and the README marks which is which. Do not read a green run
as "the notes are current".

**`.claude/notes/**` is in `docs.yml`'s path filter.** Adding checks without adding the path
would have been the worse half of the change: they would pass on every note-only commit by
never running on one.

## The check the script does not do

The roadmap's decision-gate table must cover every open question **exactly once**. Rows
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

2026-08-15 — Extended with checks 16–20 over `.claude/notes/`. **All five were proven
against deliberately broken input**, twelve breakages in total, each producing exactly one
targeted failure and the suite passing again on revert: a removed `**Owner**` row, a status
of `pending`, a heading renumbered to `NT-0009` under filename `0001`, a duplicated number,
an index status disagreeing with its file, a note missing from the index, an index row with
no file, a dangling relative link, `FR-PLAT-999`, `ADR-9999`, `NT-0042`, and a requirement
id written in the bold defining form.

Note ids are `NT-NNNN` — the short-prefix form the suite uses for `FR-`/`OQ-`/`DEP-`, at
ADR's four-digit width, with the filename carrying exactly the digits the id does.

The same pass fixed a defect the checks exposed rather than introduced: every `read_text()`
in the script was encoding-naive, so on Windows the audit crashed on the suite's first
em-dash. It had been unrunnable on the maintainer's machine while green on CI — the exact
shape of failure `reproducing-ci-locally` warns about, inverted.

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
