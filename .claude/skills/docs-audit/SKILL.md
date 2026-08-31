---
name: docs-audit
description: Verify the integrity of the docs/ specification suite and the .claude/notes/ working notes before committing or opening a PR in this GI pricing platform repo. Checks requirement IDs, cross-references, open-question mirroring, ADRs, spec sections, JSON Schemas, plus structural checks for section references, error-code ownership, dependency direction, money discipline, glossary single-sourcing and workflow coverage, the notes' header block, numbering, index agreement and references, every endpoint and pricing-core function a workflow journey cites, table-row cell counts, canonical route agreement between a module's §5.3 and `00`'s §5.6, every spec §10 mirror row's status, every F-id citation against the findings register or a closure record, the process core extract's § citations against the process spec, and every filed plan's acceptance-standard field — and the decision-gate invariant the script does not cover. The script's own module docstring is the numbered list, kept current there rather than counted here. Use before any docs commit, before any working-note commit, after applying research findings, or when asked whether the documentation is consistent or hangs together.
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

### The §10 mirrors' status (check 23)

| # | Check | The defect it catches |
|---|---|---|
| 23 | Every spec §10 mirror row carries a status token matching the register's status for that question | A mirror row left bare — question only, no status, no consequence — while the register has long since decided or deferred it |

Check 4 proves a question is mirrored in **both directions**, but nothing used to look at
what the mirror row *says* — a bare row was audit-clean by construction. OQ-OVR-7's two
bodies had diverged so far they named different things while every check passed. The
register is the source of truth: check 15 already constrains its status vocabulary, so
check 23 reads the register's status and requires the mirror row to state it in the
register's own words — "decided" (or the mirror-side "resolved" / "determined"), "open",
"deferred", "superseded".

Two deliberate scopes keep it narrow. It only scans a spec's §10 — a requirement row
citing an OQ id elsewhere in the spec is a reference, not a mirror. And it anchors to the
row: the token must follow the id on the same row, so a neighbouring row's status never
satisfies it. The row is read whole rather than first-word, because a decided row's
question text can contain a stray "open".

### Canonical routes (check 24)

| # | Check | The defect it catches |
|---|---|---|
| 24 | Every route `00` §5.6 declares canonical for a module appears in that module's own §5.3 view table (FR-OVR-22) | A module's §5.3 drops or rewrites a canonical route — drift nothing else sees, since §5.3 legitimately carries detail routes §5.6 does not list |

One-directional: `00` §5.6 is canonical, so a mismatch is always a §5.3 error, never the
other way round. Landed 2026-08-27 and had no section in this file until the 2026-08-30
pass below found the gap — the same drift this skill exists to prevent, in its own body.

### The findings register (check 25)

| # | Check | The defect it catches |
|---|---|---|
| 25 | Every `(F<n>)` / `(F-W<n>-<n>)` finding id cited in `docs/research/`, `docs/plans/` or `.claude/notes/` resolves against `docs/audit/register.md`, an archived phase register, **or a work-item closure record** (`docs/audit/work/*/README.md`, `docs/audit/closure-records.md`) | A citation to a withdrawn or not-yet-filed finding — `(F42)`, `(F45)` — reads as a real reference and nothing complains |

**Resolves against three sources, not one — a register-only first version fired on correct
behaviour, ruled wrong 2026-08-30.** `docs/audit/register.md`'s own header states its
contract: one row per *open* finding, removed when a close resolves it. A finding closed
during its own slice's audit — `F-W9-3-2`, resolved the day it was raised, recorded in
`docs/audit/work/W9-3/README.md`'s Findings table, cited from the exact spec sentence it
corrected (`03-rating-engine.md:671`) — therefore never gets a register row at all, and
treating that citation as dangling is a worse defect than the gap the check exists to catch:
it fires on every properly-closed finding cited this way. **Swept 2026-08-30** against the
real corpus: of 14 distinct F-ids cited in `docs/research/`/`docs/plans/`/`.claude/notes/`,
13 resolve via the register and exactly **1** (`F-W9-3-2`) resolves only via a closure
record — the false-positive rate a register-only design would have had, and the incident
that forced this fix.

Deliberately narrow on two further axes, both found necessary against the real corpus
rather than assumed. Only the register's own parenthesised citation form is matched — a
bare `F1` is a document's own private numbering far more often than a register reference:
several hundred hits across the W5 and W6b task plans' own "Findings" sections alone. And
only `docs/research/`, `docs/plans/` and `.claude/notes/` are scanned, never `docs/audit/`
itself (where a retired or not-yet-filed id is legitimately named in prose) or
`docs/roadmap.md`/`docs/phase-0-status.md` (a live check found the latter's `(F13)` citing
`track-a-findings.md`'s own local F13, which collides with the register's unrelated F13 —
a wider scan would have silently resolved it against the wrong row). A file citing its own
locally-defined finding — by heading, ledger-table cell, or bold paragraph lead-in, all
three seen in the real corpus — is exempt; that is self-reference, not a register citation.
The full reasoning is in the check's own docstring, `check_finding_citations` in
`scripts/audit-docs.py` — not duplicated here.

**The reverse direction — a register row citing a document that does not exist — is
deliberately not built.** A genuine markdown link inside `docs/audit/register.md` is
already check 1's, which scans all of `docs/`. Past that, the register's backtick spans
mix real paths, code symbols, `file.py:NNN` citations and error-code names with no
syntactic marker telling them apart — the same false-positive risk the citation side was
narrowed to avoid, not yet worth the same risk twice in one check.

### The process core's citations (check 26)

`docs/process/delivery-process.core.json` is the machine-readable extract of
`docs/process/delivery-process.md` (NT-0014). **The markdown is authoritative and the
extract is derived**, so the check runs one way only: an extract citing a section that does
not exist means the extract is wrong, never the spec.

Four things are checked, and the numbering deliberately skips 25 — that number is claimed
by other in-flight work, and a check number is permanent under `CLAUDE.md` §5 the way a
requirement id is.

- **Every `source` value cites at least one `§`**, and every section it names has a
  `## N.` heading.
- **`§N.M` is a *step*, not a subsection.** `delivery-process.md` has no `###` headings at
  all, so `§5.4` means step 4 of §5's numbered list. A reader who assumed subsections would
  report all eleven step citations as dangling.
- **`meta.authoritative` is `false`.** The authority rule enforced on the artifact that
  claims it, rather than only stated in the prose beside it.
- **`meta.derived_from` names a file that exists.**

**It does not skip silently when the extract is missing.** If the file is gone while
`delivery-process.md` §10 still lists it as a required artifact, that is a failure — a check
that quietly passes when its subject is deleted is one anyone can disarm by deleting it.

**What it cannot do.** A citation that resolves is not proof the cited text still says what
the citer thought (`NT-0006`: verify the claim, not just the citation). Only the mechanical
half is here, because only the mechanical half needs no judgement. The half it does catch is
the one that motivated the whole proposal: at `6f77abb` the process spec's own
back-reference named `CLAUDE.md` §12 for a pointer that lives in §15, and no gate in the
repository could see it.

### The plan acceptance standard (check 28)

Mechanises NT-0014 §2's C1 and `delivery-process.md` §5 step 4 / §6 step 1 — the lead's
replan-vs-proceed check that "an acceptance standard was actually defined, not just
implied." The field's name/position/format is defined exactly once, in
`.claude/skills/writing-plans/SKILL.md`; this check reads that shape, it does not restate
it.

**The note that raised this (NT-0014) proposed "warn until the format lands, red
thereafter" — rejected.** A time-of-run switch makes a verdict depend on *when* the check
ran rather than a fact in the file, so the same plan could pass on Tuesday and fail on
Wednesday, and a fresh clone could never reproduce which. Ruled instead
(`docs/plans/2026-08-30-nt-0014-q1-q3-q4-rulings.md`, Ruling 46): **the discriminator is
the plan's own filename date against `PLAN_ACCEPTANCE_STANDARD_CUTOFF`, a constant written
in the script** — durable and reproducible in any clone at any revision.

- **No warn phase.** C1 landed in the same commit as the `writing-plans` field it
  validates, so the cutoff is that commit's date and zero plans filed before it are ever
  in scope.
- **Never retro-red-gated.** A plan filed before the cutoff is exempt permanently, not
  temporarily — `docs/plans/README.md`'s "do not edit a filed plan to agree with today"
  rule applies to what a gate demands of it too. Legacy plans get **one aggregate note
  line** (count + cutoff date), not one warning per file — a hundred repeated warnings train
  every reader to skim past the check's output.
- **Scope is the plan *kind* only** — the suffix-less file `writing-plans` produces,
  discriminated by `docs/plans/README.md`'s four documented suffixes
  (`-ledger`/`-final-review`/`-verified`/`-handover`), never by guessing at a file's
  content. A filename with none of those suffixes and no `YYYY-MM-DD-` date prefix either
  is refused outright rather than silently classified.
- **"Defined" requires content**, not just the heading. A heading with nothing under it
  before the next heading is "implied," which §5 step 4 explicitly distinguishes from
  "defined" — that half is checked too, and reds.

**What it cannot do.** Whether the content under the heading is a *good* acceptance
standard — testable, tied to a real requirement — is not mechanised; that judgement stays
the lead's read at the replan-vs-proceed gate (`.claude/roles/lead.md`).

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

**Never name an `OQ-` id in a gate cell's explanatory italics.** Both snippets above scan the
*whole* cell, so a note reading *"raised out of the OQ-MODEL-23 and OQ-MODEL-24 decisions"* places
those two ids in that row a second time. The coverage check then reports them under
`duplicated`, and the recount counts them as **unstruck**, i.e. open — so a row genuinely holding
two open questions reports four. Both failures point at the row you added, not at the prose,
which is why this costs a while to find. Say *"the two modelling decisions taken that day"*, or
cite the requirement the decision became (`FR-MODEL-114`) — requirement ids are not scanned.
*(Found 2026-08-22, placing OQ-MODEL-23 and OQ-MODEL-24 while deciding them.)*

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

2026-08-31 — Check 28 added (every plan-kind file dated on/after the cutoff states a
non-empty "Acceptance Standard" heading) and this skill updated with it in the same commit.
Proven on deliberately broken input: a synthetic plan dated after the cutoff with no
heading reds and names the file; the same plan dated before the cutoff passes silently
(rolled into the aggregate legacy-count note line); a conforming plan dated after the
cutoff — the positive control — passes; a plan carrying the heading with nothing under it
before the next heading still reds. All four proven both as a manual gate run and as a
permanent `tests/test_audit_docs_plan_acceptance_standard.py`.

2026-08-30 (third entry, same day) — Check 26 added (the process core extract's § citations) and this skill updated with it in the same commit. Proven on deliberately broken input rather than asserted: six mutations run through `scripts/audit-docs.py` itself — a `§99` section, a `§5.99` step past §5's eight, `authoritative: true`, a `derived_from` naming no file, a `source` citing nothing, and the extract deleted while §10 still requires it. Each produced its own distinct failure, and the unmutated tree stayed silent. `.claude/skills/README.md`'s cell said "23 checks" while the code had 24; the count is now removed from that cell rather than bumped, because a restated count is `NT-0003` by construction.

2026-08-30 (second entry, same day, correcting the first) — **Check 25's first version was
itself wrong**: register-only resolution fired on `F-W9-3-2`, a real, closed, correctly-cited
finding recorded only in its slice's closure record. Ruled by the lead: resolve against the
register, an archived phase register, OR a work-item closure record
(`docs/audit/work/*/README.md`, `docs/audit/closure-records.md`) — never register-only.
**Proven both ways**: `tests/test_audit_docs_finding_citations.py` asserts a synthetic
`F999999` still fails loudly, and asserts `F-W9-3-2` stays silent — pinned against the real
tree, since that citation is the incident, not a stand-in for it. **Swept**: 1 of 14 real
citations in the scanned corpus resolves only via a closure record — the false-positive rate
the register-only version would have had.

2026-08-30 — Extended with **check 25**, F-nn citations against the findings register
(dispatched: "an F-nn cited outside the register... resolves to no row there"). Real
incident behind it: a draft cited a withdrawn F42, and F45 sat unfiled for hours after a
tombstone note first promised it, both 2026-08-29, both caught only because someone
remembered the register's actual contents rather than by anything mechanical.

Scope was narrowed twice against the real corpus, not assumed. First: a bare `F1` is not
matched, only the register's own `(F<n>)` form — a bare-token scan over `docs/plans/` and
`docs/research/` flagged several hundred false positives, every W5 and W6b task plan's own
locally-numbered "Findings" section among them. Second: `docs/roadmap.md` and
`docs/phase-0-status.md` are excluded from the scanned set even though both carry `(F..)`
tokens — a live check found `phase-0-status.md`'s `(F13)` citing
`docs/research/track-a-findings.md`'s own local F13, which collides with the register's
*unrelated* F13 and would have silently "resolved" against the wrong row rather than been
caught. A file citing its own locally-defined finding — by heading, ledger-table cell, or
bold paragraph lead-in — is exempt from the register check; the first two forms were
anticipated, the third (`docs/plans/2026-08-29-w11-1-evaluator-core.md`'s own four
findings) was found only by running the check against the real tree and reading what
failed rather than trusting the design by inspection alone.

**Proven on deliberately broken input**: a scratch file under `docs/plans/` citing a
nonexistent `(F999)` produced exactly one targeted failure naming the file and the id; the
scratch file removed, the suite passed again (module has no CLI surface of its own to test
via subprocess the way `scope-audit.py` does, so the proof is the audit-docs.py run
itself, before and after, quoted in the PR). Running the check against the real,
unmodified tree — a second, independent proof, of the check finding a genuine defect
rather than a synthetic one — surfaced a live gap: `03-rating-engine.md:598,671` cites
`(F-W9-3-2)` twice with no register row for it (only its apparent parent, `F-W9-3`,
exists), quoted once more in `docs/plans/2026-08-29-w11-slice1-rulings.md`. Not resolved
by this entry — filing a register row or correcting a citation is outside an executor's
authority — see the PR for the ruling once made.

**Two other gaps found and fixed in the same pass, both this file's own staleness**: check
24 (§5.3/§5.6 canonical routes, landed 2026-08-27) had no section here at all — added,
retroactively, from the check's own code rather than from memory. And the "number of
checks lives in three places" note further down was itself one of the three drifted
counts it was warning about, unnoticed since the 2026-08-29 entry below removed this
frontmatter's own count — corrected to two.

2026-08-29 — The module docstring's own numbered list, the code's check-numbering
comments, and this skill's description had drifted three ways: docstring stopped at 22,
code ran unbroken 1-24 (re-derived by reading each check's own logic, not by grepping the
highest numeral — the count-instead-of-read mistake this session had already caught
twice), description said "twenty-three". The 08-26 entry below shows why: twenty-three was
correct the day check 23 landed, check 24 landed the next day (08-27, `00` §5.6), and
nothing has touched either number since. **Fixed by completing the docstring** (checks 23
and 24 added, each drawn from the check's own code, not paraphrased from memory) **and by
removing the description's count outright rather than bumping it to 24** — a bare figure
with no link to what would keep it current is exactly the pattern plan review 8 named as
this drift's own worked exhibit: the drift-detection instrument drifting in its own
self-description, and then surviving being written up as the example of itself.

2026-08-26 — Extended with **check 23**, the §10 mirror rows' status, and repaired the
fifteen mirror rows it caught (finding #49's option (b)). Four were the named deferred
questions — OQ-RATE-5, OQ-OPT-1, OQ-OPT-5, OQ-MON-4 — and each got its consequence clause,
not just a status word: what deferring means for the platform (the bundle discount unpriced
and unmonitored; a challenger price never served; a `price_test` purpose the platform
refuses). The other eleven were bare rows the register had already decided or deferred
(OQ-OVR-2/16, OQ-DATA-1/2, OQ-OPT-2/3/4, OQ-MON-1/2/3/5), repaired to carry their status
and either the consequence or a pointer to the register. The register itself was untouched
— it is the source of truth the check reads.

**Proven on deliberately broken input**: removing OQ-RATE-5's status token produced exactly
one targeted failure — `03-rating-engine.md:661: OQ-RATE-5 mirror row carries no status
token matching the register's 'deferred' status` — the summary line read `115 of 116`, and
the suite passed again on restore (`116 of 116`). Two design calls are recorded in the
script's docstring: mirror-side "resolved" / "determined" count as decided (OQ-GOV-6's row
says "DETERMINED"), and the row is read whole, because a decided row's question text can
contain a stray "open".

2026-08-22 — Re-confirmed while deciding OQ-MODEL-23 and OQ-MODEL-24. `audit-docs.py` passed
throughout (495 → 499 requirements, 76 → 78 open questions), and the gate-table snippet again
reported both ids under `missing` **before** the edit — the fourth time, and the same cause as
2026-08-19: questions raised inside W5 and mirrored correctly, but never placed on the plan. The
duplicate-id-in-prose trap above was found here, and it is the first failure mode where the two
snippets disagree with each other rather than with the roadmap.

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

Also worth knowing before the next check is added: **the number of checks is stated in
two places** — `.claude/skills/README.md` and `docs.yml`'s comment — and both have to be
edited. A third, this skill's own frontmatter, used to carry a bare count too, until the
2026-08-29 entry below removed it outright rather than keep bumping it — a bare figure
with no link to what keeps it current is the exact pattern that had already drifted three
ways twice. It used to be six places in total, until `CLAUDE.md`'s three mentions were
removed: §0's own rule is that counts which change do not belong in it.

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
