---
name: docs-audit
description: Verify the integrity of the docs/ specification suite and the .claude/notes/ working notes before committing or opening a PR in this GI pricing platform repo. Runs twenty-two checks — requirement IDs, cross-references, open-question mirroring, ADRs, spec sections, JSON Schemas, plus structural checks for section references, error-code ownership, dependency direction, money discipline, glossary single-sourcing and workflow coverage, the notes' header block, numbering, index agreement and references, every endpoint and pricing-core function a workflow journey cites, and table-row cell counts — and the decision-gate invariant the script does not cover. Use before any docs commit, before any working-note commit, after applying research findings, or when asked whether the documentation is consistent or hangs together.
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

Check 22 is silent when it passes — it has no count worth printing, and a table whose
rows all match their header is the unremarkable case.

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

### The journeys' citations (check 21)

| # | Check | The defect it catches |
|---|---|---|
| 21 | Every `` `METHOD /path` `` and `` `name()` `` in `wf-01…05` is declared in a spec's §5.1 or §5.2 | A journey citing an interface no spec declares — renamed, never written, or removed under it |

FR-OVR-17(i), and `scope-audit.py --endpoints` one level up: that compares a spec's table
against the published contract, this compares the **journeys** against the specs. Check 14's
"workflow coverage" is a different and much weaker question — whether a journey *mentions* a
requirement id.

**Citations only count if they are recognisable, so the form is fixed** in
`docs/workflows/README.md`: an endpoint is `` `METHOD /path` `` without the `/api/v1` prefix,
a function is `` `name()` `` **with the parentheses**. Without the parentheses the check would
have to guess at every backticked token in a `Worker → pricing-core` row, and those rows also
contain `` `control` ``, `` `_rejected` ``, `` `f` ``, `` `where` `` and `` `Piecewise` ``.

**A declared `{}` segment matches a literal one**, but only after an exact match fails. A
journey writes `/environments/prod/deployments` where `03` §5.1 declares
`/environments/{env}/deployments`, and the journey is right to be concrete. The audit prints
how many citations used that fallback, because it is the one place the check is looser than a
strict comparison — a citation of `/models/nonsense` would match a declared `/models/{}`.

**Read the summary line, not just the exit code.** It reports the counts and says
`**N undeclared**` rather than `all declared` when the check failed — a note claiming
correctness above a `FAILED` block is the shape of defect this audit exists to catch.

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

**The `N (M open)` count in the third column is hand-maintained, and nothing above checks it.**
`spec-change` says to *recount* a row rather than decrement it; this recounts every row, reading
a struck id (`~~OQ-…~~`) as decided and an unstruck one as open:

```bash
python3 - <<'PY'
import re, pathlib
gate = pathlib.Path('docs/roadmap.md').read_text(encoding='utf-8').split('## 10. Decision gates')[1].split('## 11.')[0]
for row in [l for l in gate.splitlines() if l.startswith('| ') and 'OQ-' in l]:
    cells = row.split('|')
    ids = {}
    for m in re.finditer(r'(~~)?OQ-([A-Z]+)-(\d+)(?:\.\.(\d+))?(~~)?', cells[2]):
        a, b = int(m.group(3)), m.group(4)
        for n in range(a, (int(b) if b else a) + 1):
            ids[f"OQ-{m.group(2)}-{n}"] = 1 if m.group(1) else 0
    total, decided = len(ids), sum(ids.values())
    print(f"{cells[1].strip()[:40]:42s} actual {total} ({total - decided} open)  stated {cells[3].strip()}")
PY
```

Every `actual` must equal its `stated`. A range written `OQ-GOV-1..5` counts as five, and a range
struck as a whole counts five decided — which is how the rows are actually written.

**`duplicated` fires on prose inside a table row, not only on a real second placement.** The
Phase 3 row carried a parenthetical — *(OQ-GOV-7 is gated at 1b, not here — see below)* — and
the snippet counts ids per row, so an id was placed twice by a note whose whole purpose was
to say it was placed once. Keep cross-gate notes in the prose **beneath** the table, where no
row can claim them. Found 2026-08-18, together with four ids the table was missing outright.

**`missing` is the expensive one, and it does not clear itself.** OQ-MODEL-12, OQ-MODEL-13,
OQ-MODEL-14 and OQ-GOV-8 were each raised in a spec, correctly mirrored into
`open-questions.md`, and invisible to the plan — `audit-docs.py` passed throughout, because it
checks the spec ↔ register mirror and cannot see the roadmap at all. Two of the four were
decided on the day they were finally placed, which is the point: a question the plan never
saw cannot be scheduled, so it gets answered by whoever trips over it.

## Adding a check

Extend `scripts/audit-docs.py` — it is production code, not a scratch script. **Verify a
new check by feeding it deliberately broken input and confirming it fails**, otherwise a
silently passing no-op check is worse than no check.

## When a check fails

Do not weaken the check to make it pass. Broken links and unmirrored open questions are
real defects; fix the document.

## Verified

2026-08-19 — Confirmed while recording OQ-DATA-9 (→ FR-DATA-50, FR-DATA-51). The script passed
before and after; the gate-table snippet reported `missing: ['OQ-DATA-9']` **before** the edit — a
question raised in W5 on 2026-08-18, correctly mirrored into the register, and never placed on the
plan, so the gate it belonged to had already closed by the time it was decided. That is the third
time the `missing` half has caught a question the plan could not see, and the first where the cost
was legible: an unplaced question is never scheduled, so it gets answered by whoever trips over it.
The count-recount snippet above was written here, because striking an id and leaving `12 (0 open)`
alone is the silent half of the same edit.

2026-08-18 — Confirmed while recording five maintainer decisions (OQ-MODEL-10..13, OQ-GOV-7).
The script passed before and after; the **gate-table snippet did not**, and the two failures it
reported are written up above. Run the snippet at every raise *and* every decision — a decided
question still needs a row, because a row is where the revisit is scheduled.

2026-08-17 — Extended with **check 21**, the journeys' interface citations (FR-OVR-17(i)).
Proven on deliberately broken input in both halves — an undeclared endpoint and an undeclared
function each produced exactly one targeted failure, and the summary line's verdict flipped
with them. **It found a real defect on its first run**: wf-01 cited `profile_version()`, which
`01` §5.2 renamed to `profile_frame` / `profile_parquet` on 2026-08-15 without the journey
following.

Also worth knowing before the next check is added: **the number of checks is stated in six
places** — `CLAUDE.md` three times, this skill's frontmatter, `.claude/skills/README.md`, and
`docs.yml`'s comment — and every one of them had to be edited. `CLAUDE.md` §0's own rule is
that counts which change do not belong in it.

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
