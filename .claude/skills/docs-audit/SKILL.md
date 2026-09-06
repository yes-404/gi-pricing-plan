---
name: docs-audit
description: Verify the integrity of the docs/ specification suite and the docs/notes/ working notes before committing or opening a PR in this GI pricing platform repo. Checks requirement IDs, cross-references, open-question mirroring, ADRs, spec sections, JSON Schemas, plus structural checks for section references, error-code ownership, dependency direction, money discipline, glossary single-sourcing and workflow coverage, the notes' header block, numbering, index agreement and references, every endpoint and pricing-core function a workflow journey cites, table-row cell counts, canonical route agreement between a module's §5.3 and `00`'s §5.6, every spec §10 mirror row's status, every F-id citation against the findings register or a closure record, the process core extract's § citations against the process spec, and every filed plan's acceptance-standard field — and the decision-gate invariant the script does not cover. The script's own module docstring is the numbered list, kept current there rather than counted here. Use before any docs commit, before any working-note commit, after applying research findings, or when asked whether the documentation is consistent or hangs together.
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
| 11 | Dependencies respect DEP-1 / DEP-537 | A spec's §7.1 lists a module to its right, inverting the build order |
| 12 | `*_minor` fields are never fractional | A money example written as `361.20` violates FR-10 |
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
| 17 | Note numbering: `NNNN-kebab.md`, unique, matching the `NT-NNNN` heading | A number reused or a heading that disagrees with its filename, so an `RFC-712` reference points at two things |
| 18 | The `docs/rfcs/README.md` index and the directory agree, both ways | A note added and never indexed, or an index row outliving its file |
| 19 | Every link, `FR-`/`NFR-`, `OQ-`, `ADR-` and `NT-` reference in a note resolves | A note citing a requirement — or a superseding note — that never existed, which reads exactly like one that does |
| 20 | No note defines a requirement id in the bold `**FR-…**` form | A requirement escaping `docs/specs/`, where `CLAUDE.md` §5's permanence rule does not reach it |

**Checks 16–20 cover the mechanical half of `docs/rfcs/README.md`'s audit standard.**
The other half — is this status still *true*, is this deliverable still right for the
current phase — is judgement, and the README marks which is which. Do not read a green run
as "the notes are current".

**`docs/notes/**` is in `docs.yml`'s path filter.** Adding checks without adding the path
would have been the worse half of the change: they would pass on every note-only commit by
never running on one.

### The journeys' citations (check 21)

| # | Check | The defect it catches |
|---|---|---|
| 21 | Every `` `METHOD /path` `` and `` `name()` `` in `WF-698…05` is declared in a spec's §5.1 or §5.2 | A journey citing an interface no spec declares — renamed, never written, or removed under it |

FR-19(i), and `scope-audit.py --endpoints` one level up: that compares a spec's table
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
what the mirror row *says* — a bare row was audit-clean by construction. OQ-544's two
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
| 24 | Every route `00` §5.6 declares canonical for a module appears in that module's own §5.3 view table (FR-25) | A module's §5.3 drops or rewrites a canonical route — drift nothing else sees, since §5.3 legitimately carries detail routes §5.6 does not list |

One-directional: `00` §5.6 is canonical, so a mismatch is always a §5.3 error, never the
other way round. Landed 2026-08-27 and had no section in this file until the 2026-08-30
pass below found the gap — the same drift this skill exists to prevent, in its own body.

### The findings register (check 25)

| # | Check | The defect it catches |
|---|---|---|
| 25 | Every `(F<n>)` / `(F-W<n>-<n>)` finding id cited in `docs/research/`, `docs/plans/` or `docs/notes/` resolves against `docs/findings/register.md`, an archived phase register, **or a work-item closure record** (`docs/audit/work/*/README.md`, `docs/closures/INDEX.md#closure-recordsmd`) | A citation to a withdrawn or not-yet-filed finding — `(F42)`, `(F45)` — reads as a real reference and nothing complains |

**Resolves against three sources, not one — a register-only first version fired on correct
behaviour, ruled wrong 2026-08-30.** `docs/findings/register.md`'s own header states its
contract: one row per *open* finding, removed when a close resolves it. A finding closed
during its own slice's audit — `F-W9-3-2`, resolved the day it was raised, recorded in
`docs/closures/CR-00837-work-item-record-w9-3-bundle-compilation.md`'s Findings table, cited from the exact spec sentence it
corrected (`03-rating-engine.md:671`) — therefore never gets a register row at all, and
treating that citation as dangling is a worse defect than the gap the check exists to catch:
it fires on every properly-closed finding cited this way. **Swept 2026-08-30** against the
real corpus: of 14 distinct F-ids cited in `docs/research/`/`docs/plans/`/`docs/notes/`,
13 resolve via the register and exactly **1** (`F-W9-3-2`) resolves only via a closure
record — the false-positive rate a register-only design would have had, and the incident
that forced this fix.

Deliberately narrow on two further axes, both found necessary against the real corpus
rather than assumed. Only the register's own parenthesised citation form is matched — a
bare `F1` is a document's own private numbering far more often than a register reference:
several hundred hits across the WK-661 and WK-664 task plans' own "Findings" sections alone. And
only `docs/research/`, `docs/plans/` and `docs/notes/` are scanned, never `docs/audit/`
itself (where a retired or not-yet-filed id is legitimately named in prose) or
`docs/roadmap.md`/`docs/closures/CR-00709-phase-0-specification-status.md` (a live check found the latter's `(F13)` citing
`track-a-findings.md`'s own local F13, which collides with the register's unrelated F13 —
a wider scan would have silently resolved it against the wrong row). A file citing its own
locally-defined finding — by heading, ledger-table cell, or bold paragraph lead-in, all
three seen in the real corpus — is exempt; that is self-reference, not a register citation.
The full reasoning is in the check's own docstring, `check_finding_citations` in
`scripts/audit-docs.py` — not duplicated here.

**The reverse direction — a register row citing a document that does not exist — is
deliberately not built.** A genuine markdown link inside `docs/findings/register.md` is
already check 1's, which scans all of `docs/`. Past that, the register's backtick spans
mix real paths, code symbols, `file.py:NNN` citations and error-code names with no
syntactic marker telling them apart — the same false-positive risk the citation side was
narrowed to avoid, not yet worth the same risk twice in one check.

### The process core's citations (check 26)

`docs/process/delivery-process.core.json` is the machine-readable extract of
`docs/process/delivery-process.md` (RFC-895). **The markdown is authoritative and the
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
the citer thought (`RFC-779`: verify the claim, not just the citation). Only the mechanical
half is here, because only the mechanical half needs no judgement. The half it does catch is
the one that motivated the whole proposal: at `6f77abb` the process spec's own
back-reference named `CLAUDE.md` §12 for a pointer that lives in §15, and no gate in the
repository could see it.

### The plan acceptance standard (check 28)

Mechanises RFC-895 §2's C1 and `delivery-process.md` §5 step 4 / §6 step 1 — the lead's
replan-vs-proceed check that "an acceptance standard was actually defined, not just
implied." The field's name/position/format is defined exactly once, in
`.claude/skills/writing-plans/SKILL.md`; this check reads that shape, it does not restate
it.

**The note that raised this (RFC-895) proposed "warn until the format lands, red
thereafter" — rejected.** A time-of-run switch makes a verdict depend on *when* the check
ran rather than a fact in the file, so the same plan could pass on Tuesday and fail on
Wednesday, and a fresh clone could never reproduce which. Ruled instead
(`docs/rulings/RL-00906-q3-never-retro-red-gate-adopted-warn-until-the-format-lands-red-thereafter-rejected-as-the-mechanism.md`, RL-906): **the discriminator is
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

### The notes tombstone — retired, moved to check 36 (2026-09-02)

Checks 30-39 below are RFC-937's id-standard audit
(`docs/rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md` §1.11). Slot **30** collided with the
tombstone check this section used to describe: RFC-937 §5.5 resolves the collision by
**replacing** the tombstone check rather than renumbering either one —
`check_notes_tombstone` was renamed `check_redirects` and moved to slot **36**, whose
job is now watching `docs/REDIRECTS.csv` instead of the `.claude/notes/` stub set this
section used to describe in detail. The stub-watching mechanism (18 registered
basenames, byte-exact template comparison, `tests/test_audit_docs_notes_tombstone.py`)
is gone with it — read `git log -p -- scripts/audit-docs.py` at the commit before this
one if the old mechanism's exact shape is ever needed again. The number 30 is not
reused for two things (`CLAUDE.md` §5); see the section below for what occupies it now.

### RFC-937's id-standard checks (30-39)

The full ten-item list, and what each one catches, is `scripts/audit-docs.py`'s own
module docstring — kept current there, per this skill's own rule, rather than restated
here where it would go stale a second way. Six things worth knowing before reading
that docstring:

- **Path-scoped, not corpus-wide, until the migration lands.** A single module-level
  constant, `_ID_SCOPE_ROOTS`, bounds every one of the ten checks to
  `docs/_templates/` and `docs/process/document-ids.md` — the only things the standard
  has actually touched so far. Slice W37-6 (the migration) widens it to the whole
  corpus in the same commit that migrates (D14: "enforcement red from the migration
  PR" — no warn phase, no date switch). Before that, the checks would otherwise red on
  every pre-migration id form the rest of the repository still uses.
- **`docs/_templates/` is read as a policy *source*, never validated as a document.**
  Check 30's per-family field policy (which fields are permitted/required) and check
  37's per-family required sections are both *derived* from the templates' own content
  (RL-981) rather than hand-transcribed from RFC-937 §1.5's prose, which the ruling
  found diverges from the templates in both directions. `derive_field_policies()`
  asserts its own coverage against a hardcoded manifest of all thirteen template
  filenames — a template silently going missing, or losing its front-matter block,
  fails loudly rather than reading as a smaller, equally-plausible-looking policy.
- **Two checks are gated on an artifact that does not exist yet, on purpose.** Check
  32 (citation resolution) needs `docs/INDEX.md`; check 36's legacy-form sweep needs
  `docs/REDIRECTS.csv`. Both are post-migration invariants — before migration, a
  legitimate citation to a not-yet-renumbered thing (`docs/process/document-ids.md`'s
  own lift of RFC-937 cites `RFC-897`, `RFC-896`, `RL-943`, `docs/audit/` in its own
  prose) is indistinguishable from a "survivor" by pattern alone. Both checks skip with
  a note, not silently, when their artifact is absent.
- **Four checks carry a specific ruling's mechanism**: check 30 (RL-981's
  template-derived field policy), check 33 (RL-983's map-plan roll-up raise — it
  calls `doc-index.py`'s own `derive_execution` and surfaces the `ValueError` its
  precedence table's "no catch-all" last row produces, rather than re-implementing the
  table), check 34 (DP-7's freeze predicate, `frozen_diff_is_permitted`, exported at
  module level so a later migration-diff filter can call the identical function), and
  check 36 (RL-988/DP-2's legacy-form pattern and exclusion list, `sweep_legacy_forms`
  — one shared, explicit-parameter function, reused unscoped once the corpus migrates).
- **Check 39's corpus build is guarded (F76, 2026-09-02) — it is not optional.**
  `check_index_stable` is the *tenth and last* of `check_ids_30_39()`'s ten calls, and
  `main()` runs six further checks immediately after it with no exception boundary
  between any of them (`check_open_question_mirror_status`, `check_finding_citations`,
  `check_process_core_drift`, `check_process_core_digest`,
  `check_plan_acceptance_standard` [check 28], `check_register_grammar` [check 29]). An
  uncaught exception building the corpus there used to abort the whole script before
  any of those six ever ran, and before the `notes`/`failures` every check that already
  ran had accumulated were ever printed — a traceback instead of a report, during
  exactly the commit (W37-6) that stamps 304 headers for the first time. Guarded
  against `_doc_index.HeaderError` (a malformed header, whole-document or row-block) and
  `ValueError` (`doc-index.py`'s own row-block `created:` parsing is unguarded, unlike
  `_docid.py`'s whole-document one). **The trap in writing the guard itself**:
  `doc-index.py` reloads `scripts/_docid.py` under its own module instance
  (`scripts/doc-index.py:85-90`) rather than sharing this script's, so
  `_doc_index.HeaderError` and this script's own `_docid.HeaderError` are two distinct
  class objects built from identical source — `_docid.HeaderError is
  _doc_index.HeaderError` is `False`. An `except _docid.HeaderError:` guard around a
  `_doc_index` call type-checks under mypy and silently fails to match at runtime; catch
  the exception type the module that actually raises it exports.
- **Every one of the ten states an explicit count, and zero is a numeral, never just
  "skipped."** Checks 30, 33 and 37 currently examine the corpus's one real
  document (`document-ids.md`); checks 31, 32, 34, 36, 38 and 39 currently examine
  zero. Check 35 examines that same one document for `owner:` **and** reconciles F83's
  exemption register against RFC-937's whole stamp set, so its note carries three
  numbers, not one — the register is live at full corpus width while the id checks
  around it are still scoped to two roots. A check that examines zero documents and passes is indistinguishable from a
  check that works unless its own note says so — `test_every_check_30_to_39_reports_how_many_documents_it_examined`
  (`tests/test_audit_docs_ids.py`) pins this against the real, unmodified tree, and
  scans past each note's own `check N:` prefix before looking for a digit (the prefix's
  own number would otherwise satisfy a naive digit-scan trivially, on every check,
  whether or not it ever states a count).

- **`audit-docs.py` now needs a git repository** — its first such dependency, added
  with F83's exemption register (check 35). Run outside a repository, or with no `git`
  on `PATH`, check 35 reports `cannot enumerate RFC-937's stamp set: …` and the gate
  reds. **That failure is deliberately loud rather than skipped**, because an unreadable
  corpus yields zero unstampable files, and zero reconciles against any register exactly
  as cleanly as a correct one.
- **Why a git shell-out in a docs linter, and not the obvious `rglob`.** This is the
  question the next reader will ask, so the answer is recorded rather than left to be
  re-derived: **a working-tree walk is not a function of the tree.** It picks up
  `.venv/`, `graphify-out/`, editor droppings and anything else untracked, so two
  checkouts of the *same commit* enumerate different corpora and the register reconciles
  in one and not the other. `git ls-files` is the only enumeration that depends on the
  commit alone. `scripts/file-census.py` measured this and `scripts/doc-id.py` records
  it as settled — *"the corpus is `git ls-files`, never a working-tree walk"* — which is
  why `nt0019_stamp_set` reuses `file-census.py`'s helper instead of growing a third
  copy. **Reaching for the walk is the reversal to resist**, and it will look like a
  simplification when someone does.
- **Adding a file that cannot carry a header means adding it to the register**
  (`UNSTAMPABLE_EXEMPTIONS` in `scripts/audit-docs.py`) with its reason and its ruling —
  a new `.json` or `.yaml` under `docs/` reds check 35 by name until you do. That is
  F83 condition 2 working as designed, not an obstacle: the register is enumerated as
  literal paths rather than matched by a directory-and-extension rule precisely so the
  population cannot grow without someone deciding that it should.

Ten broken-input proofs (one per check) and every ruling-specific mechanism proof live
in `tests/test_audit_docs_ids.py`, alongside the fixtures under
`tests/fixtures/docs-ids/w37-4-checks/` and `tests/fixtures/docs-ids/w37-4-rollup-raise/`.

### Validating a set of counts — a total validates the total, and nothing else

**A sum is invariant under a transfer between buckets, so checking a total cannot detect a
compensating error.** Added 2026-09-02 after the lead did exactly that.

An agent reported six class counts summing to 98. The lead verified them by confirming the sum.
It was 98. **So was the correct set** — two buckets had moved by 2 in opposite directions. The
wrong figures were then published in a maintainer-facing document on the strength of that check.
**The check was not unlucky; it was structurally incapable**, because the quantity it examines
cannot vary with the defect it was meant to catch.

**The test to apply before trusting any verification:** *can the number I am checking change when
the error I am looking for is present?* If not, the check is theatre however carefully it is run.

**This repository already had the rule and the weaker thing was done anyway.** RL-985 requires
a census to refuse by **naming every unmatched unit, never by comparing counts** — its own stated
reason being that a count cannot distinguish a true zero-gap from two mismatched miscounts that
cancel. That is the same failure, and the ruling had been cited repeatedly the same day.

**So, for any bucketed count: check membership, not the total.** Name the units in each bucket, or
diff the enumeration. A sum is fit for catching a **loss**, not a **transfer**. When someone hands
you a set of counts, the useful question is not *"do these add up"* but *"which rows produced each
one"*.

**And derive rather than re-check.** The error was found by its author re-building the list from
the rows, not by re-adding the summary line — a second pass over the same summary reproduces the
same mistake. This is why `_reconcile_census` names units and why the ruling-acceptance-item census
script asserts bucket membership instead of confirming a printed total.

### Validating a marker count — a marker count validates the marker, and nothing else

**A labelled clause is one way to state a testable failure condition, not the only way, so
counting the label undercounts the property.** Added 2026-09-02, found while checking whether
26 `CONSTRUCTIBLE` rows in the ruling acceptance-item sweep might be riding on a section's
position rather than each carrying its own check — the same shape a sibling finding that day
found in a register script's weak proxy.

The check built for it: count labelled `*Violation:` clauses in a ruling's acceptance section
and compare against the item count its own summary claims. Two rulings (79, 80) came back
short — three items claimed, one and two clauses found. **Read both in full rather than filing
the mismatch, and both were false alarms.** RL-998 §4's first and third items state their
failure condition as *"must fail today... with `unknown row field 'tree'`"* and *"it must
red"* — genuine, testable claims, just not carrying the literal word the count was built to
find. RL-999 §4 has the identical shape. All six items across both rulings hold; the count
was wrong, not the rulings.

**The test to apply before trusting a marker count:** *is the marker itself the property, or
only one way of stating it?* If an unlabelled phrasing can express the same claim — and here
it plainly does — a count of the label measures the label's popularity, not the property's
presence. This is the same failure as `scripts/register-lint.py`'s `check_unowned_decay`
(`_UNOWNED_MIN_LEN`, a length proxy for "names an event"): a marker's **presence** stood in
for the **property** the marker is supposed to indicate, in both directions — absent here
(the property held without the marker), weak there (the marker fired without the property).

**So, for any labelled-clause count: read what the count excludes before trusting what it
includes.** A shortfall is real evidence something may be missing, but only a read of the
actual text distinguishes "the item never stated a violation" from "the item stated one
without the label" — the same distinction Rulings 21 and 51 required by hand, because a
mechanical marker cannot draw it. A count that fires and is overruled on a full read is
working; the failure mode is filing the count without reading past it.

## The check the script does not do

The roadmap's decision-gate table must cover every open question **exactly once**. Rows
use the compact range form `OQ-633, OQ-634, OQ-635, OQ-636, OQ-637`:

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

Every `actual` must equal its `stated`. A range written `OQ-633, OQ-634, OQ-635, OQ-636, OQ-637` counts as five, and a range
struck as a whole counts five decided — which is how the rows are actually written.

**Never name an `OQ-` id in a gate cell's explanatory italics.** Both snippets above scan the
*whole* cell, so a note reading *"raised out of the OQ-571 and OQ-572 decisions"* places
those two ids in that row a second time. The coverage check then reports them under
`duplicated`, and the recount counts them as **unstruck**, i.e. open — so a row genuinely holding
two open questions reports four. Both failures point at the row you added, not at the prose,
which is why this costs a while to find. Say *"the two modelling decisions taken that day"*, or
cite the requirement the decision became (`FR-209`) — requirement ids are not scanned.
*(Found 2026-08-22, placing OQ-571 and OQ-572 while deciding them.)*

**`duplicated` fires on prose inside a table row, not only on a real second placement.** The
Phase 3 row carried a parenthetical — *(OQ-639 is gated at 1b, not here — see below)* — and
the snippet counts ids per row, so an id was placed twice by a note whose whole purpose was
to say it was placed once. Keep cross-gate notes in the prose **beneath** the table, where no
row can claim them. Found 2026-08-18, together with four ids the table was missing outright.

**`missing` is the expensive one, and it does not clear itself.** OQ-584, OQ-585,
OQ-586 and OQ-632 were each raised in a spec, correctly mirrored into
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

2026-09-02 (eighth entry, same day) — **the selector entry above is superseded: `F87` is
fixed.** `_id_scope_documents` no longer expands a directory root with `rglob("*.md")`. It
expands it through `_docid.stamp_set_files`, the filesystem face of RFC-937 §4 step 5's
stamp-set predicate — the same `_docid.in_stamp_set` that `nt0019_stamp_set` reads, so the
enforced scope and the corpus the F83 register is reconciled against are now one
definition with two consumers, in `scripts/audit-docs.py` and `scripts/doc-id.py`. A scope
widened to the four post-migration roots now reaches **all 65** register entries, the 62
non-`.md` files included, and check 30 consults `UNSTAMPABLE_EXEMPTIONS` and passes them
rather than redding on every one. **`_ID_SCOPE_ROOTS` itself is unchanged** — still S1's
two paths — so both changes are inert until the roots widen, which is the point: the
mechanism is proven before the irreversible commit, not inside it. Pinned by
`test_widening_the_scope_roots_reaches_every_non_markdown_file_the_register_exempts`,
`test_check_30_passes_a_registered_unstampable_file_that_is_now_in_scope` and
`test_the_two_stamp_set_consumers_read_one_definition` (set equality over the real corpus,
with its own broken-input proof), which replace
`test_widening_the_scope_roots_alone_reaches_no_non_markdown_file`. The stamp set is
**430** at `32fc63c`, of which **62** are non-markdown; predicate
`_docid.nt0019_stamp_set(tracked)` with `tracked` from
`git ls-tree -r --name-only 32fc63c`. Tree `32fc63c`.

2026-09-02 (seventh entry, same day) — the selector, not the asserts. Widening
`_ID_SCOPE_ROOTS` does **not** widen what checks 30-39 see to non-markdown files:
`_id_scope_documents` walks a directory root with `rglob("*.md")`, so a scope widened to
`docs/` collects 583 paths and reaches **3** of the register's 65 — the vendored manifests
— and none of the 62 non-`.md` files. Measured, not reasoned about, and pinned at the time by
`test_widening_the_scope_roots_alone_reaches_no_non_markdown_file`. **Superseded by the
eighth entry above, which fixed it**; kept because it is the record of what was believed. Check 35's
second reconciliation clause was also proven by **simulating** the widened scope rather
than waiting for it — red in bulk pre-migration (D14), green post-migration, red by name
when one register entry is dropped, green when restored. Tree `f61f9a4`.

2026-09-02 (sixth entry, same day) — check 35 gained F83's exemption register: the 65 files in
RFC-937's stamp set that cannot carry a YAML front-matter header, each citing its reason and the
ruling that permits it, reconciled against the tree **by name** so the list cannot grow silently.
Two of the 65 were surfaced by the check itself and are not in the 63 F83's census measured
(`docs/process/delivery-process.core.json`, `docs/research/file-census-5ef559d.csv`) — condition 2
earning its place on the day it landed. The section §*"Validating a set of counts — a total
validates the total, and nothing else"* is why the reconciliation names both sides of the
disagreement instead of comparing two totals — cited by name rather than by position, because
this block gains entries and a "two entries above" pointer stops resolving the moment one lands,
which is what happened to this very sentence. Proven by mutating the register so the two totals
cancel exactly, where a total-only implementation reports nothing at all. Tree `f61f9a4`.

2026-09-02 (fifth entry, same day) — marker-count rule added: *"a marker count validates the
marker, and nothing else."* Sibling to the total-validates-total entry below, found the same
day auditing whether the same shape of weak check reached 26 rows of a separate sweep. Two
apparent shortfalls (Rulings 79 and 80: three items claimed, one and two labelled `Violation:`
clauses found) both cleared on a full read — the missing items stated their failure condition
without the literal label. The count was the thing that was wrong, not the rulings; recorded
so the next mechanical count of a label is read past before it is trusted. Tree `c0739ac`.

2026-09-02 (fourth entry, same day) — counting rule added: *"a total validates the total, and
nothing else."* Recorded because the lead validated a set of six bucket counts by confirming they
summed to 98, which they did — and so did the correct set, two buckets having moved by 2 in
opposite directions. The wrong figures reached a maintainer-facing document. The rule already
existed as RL-985's naming-not-counting property; what was missing was its statement as a
**verification** discipline rather than a **census** one, so the section states the test to apply
to any check before trusting it. Tree `ba31cd1`.

2026-09-02 (third entry, same day) — F76 fixed: `check_index_stable`'s
`_doc_index.build_corpus(ROOT)` call, the tenth and last of `check_ids_30_39()`'s ten
calls, was unguarded — an uncaught `_doc_index.HeaderError` or `ValueError` there
aborted `main()` before the six checks it runs immediately afterward (see the new
bullet in the section above), and before any note the checks that already ran had
accumulated was ever printed. **Proven both ways, real tree and permanent test**: with
the guard removed, appending a `WK-9999` row block carrying an unknown field to the
real `docs/roadmap.md` and running `python3 scripts/audit-docs.py` end to end produced a
21-line traceback and nothing else — no notes, no `FAILED` list, no
"All checks passed." — reverted with `git checkout --`; with the guard applied, the
identical mutation produced the full structured report (all of checks 1-38's notes,
plus `check_open_question_mirror_status`, `check_finding_citations`,
`check_process_core_drift`, `check_process_core_digest`, check 28 and check 29 running
normally) with exactly one clean failure naming the corpus build error. Permanent
proofs in `tests/test_audit_docs_ids.py`: two broken-input fixtures (an unknown row
field — deliberately not `tree`, RL-998's own in-flight fix target, which would stop
reproducing `HeaderError` the moment that lands — and a non-ISO `created:`, which is
`ValueError`, not `HeaderError`, and would slip past a guard scoped to the latter
alone), an orchestrator-level proof that `check_ids_30_39()` itself completes rather
than raising, and a direct identity check that `_docid.HeaderError is not
_doc_index.HeaderError` (the trap named in the section above). Same commit: checks 32,
38 and 39's zero-population notes rewritten to state an explicit "0" rather than only
"skipped"/"nothing to warn about"/the word "zero", and check 39's byte-stable/stale
notes extended to state the record count too — pinned by a new
`test_every_check_30_to_39_reports_how_many_documents_it_examined`, itself first written
with a digit-scan bug (the check number in a note's own `check 32:` prefix already
contains digits, so scanning the whole string passed trivially regardless of whether a
count was ever stated) that was caught only by reverting the fix and confirming the
test actually reds — the same "prove the proof is not vacuous" discipline check 39's
own guard proof used.

2026-09-02 — Checks 30-39 added (RFC-937's id-standard audit, Slice W37-4,
`docs/plans/PL-00939-wk-697-one-id-per-governed-thing-map-plan.md`), path-scoped to
`_ID_SCOPE_ROOTS` until the migration (Slice W37-6) widens it. Slot 30 changed
identity: `check_notes_tombstone` moved to slot 36 and became `check_redirects` (RFC-937
§5.5); its old test file, `tests/test_audit_docs_notes_tombstone.py`, is deleted, per
RFC-937 §5.7, and its "always name the old path" citation is folded into
`tests/test_audit_docs_ids.py` (see `tests/test_notes_move_citations.py`'s
`_CHECK_30_MECHANISM`, itself renamed in the same commit to reflect the move). Two
defects found and fixed while building this: `citation_problems_in_file`'s padding
check compared against `_docid.ID_RE`'s captured number group, which the regex's own
`0*` already strips of its leading zero before the group ever sees it, so a padded
citation could never be detected — fixed by comparing the *full match* against the
canonical form instead. And `python3 scripts/doc-index.py --check` exited 1
unconditionally when `docs/INDEX.md` did not exist, which would have red the two new
`docs.yml` gate steps this slice wires in on every push until the migration lands —
fixed to exit 0 when the corpus is also empty (pre-migration), 1 when records exist but
the index does not (genuinely stale), proven by both cases in `tests/test_doc_index.py`.
**Proven on deliberately broken input, one fixture per check**, plus the ruling-specific
mechanisms named in the section above — see `tests/test_audit_docs_ids.py`'s own module
docstring for the pairing.

2026-09-02 — The check-30 section above, and the 2026-09-01 entry below, both said
`audit-docs.py`'s positive-control test asserts the literal "18 working notes". That was
only ever true because the tombstone's 18 frozen stubs and `docs/notes/`'s then-current
file count happened to coincide the day this check was verified — two disjoint counts
(the note above already says why) that did not stay equal. RFC-937, filed the next day
(PR #555), grew `docs/notes/` to 19 and broke the hardcoded literal in
`tests/test_audit_docs_notes_tombstone.py::test_the_unmodified_tombstone_passes` within a
day of it being written — the same "duplicated count goes stale" failure mode `CLAUDE.md`
already names (`RFC-756`), landing inside a test rather than a doc this time. Fixed by
deriving the expected count from `docs/notes/*.md` (excluding `README.md`) at run time,
the same rule `check_notes()` itself uses, instead of restating a number. **Proven on
deliberately broken input**: temporarily changing `check_notes()`'s own count line to
print one more than the real count reproduces a red failure (the test's independent
recount catches the mismatch); reverted, the suite is green again. The section above is
corrected to match; this entry is the record of why, left in place rather than silently
edited into the 2026-09-01 entry below, which was an accurate report of what was true that
day and is kept as written.

2026-09-01 — Check 30 added (the vacated `.claude/notes/` tombstone: exactly the
README plus a frozen, closed set of 18 per-file redirect stubs, each byte-identical
to a rendered template). RL-951
(`docs/rulings/RL-00951-rl-947-s-tombstone-gains-per-file-stubs-watched-by-a-new-check-not-left.md`), raised when
RFC-897 Slice 4's own execution found the ruled single-README tombstone (RL-947)
does not keep 13 frozen plans' individual old-path note citations resolving on disk
(check 1), and the stub files built to fix that were watched by nothing once `NOTES`
moved to `docs/notes/`. **Proven on deliberately broken input, both cases the ruling
names**: a stray file added at the old path fails, naming the file, before its content
is read; an edited stub body (a sentence appended) fails, naming the file and the
mismatch. Both reproduced as `tests/test_audit_docs_notes_tombstone.py`, alongside a
positive-control test that the unmodified tombstone stays silent and `audit-docs.py`
still reports 18 working notes.

2026-08-31 — Check 28 added (every plan-kind file dated on/after the cutoff states a
non-empty "Acceptance Standard" heading) and this skill updated with it in the same commit.
Proven on deliberately broken input: a synthetic plan dated after the cutoff with no
heading reds and names the file; the same plan dated before the cutoff passes silently
(rolled into the aggregate legacy-count note line); a conforming plan dated after the
cutoff — the positive control — passes; a plan carrying the heading with nothing under it
before the next heading still reds. All four proven both as a manual gate run and as a
permanent `tests/test_audit_docs_plan_acceptance_standard.py`.

2026-08-30 (third entry, same day) — Check 26 added (the process core extract's § citations) and this skill updated with it in the same commit. Proven on deliberately broken input rather than asserted: six mutations run through `scripts/audit-docs.py` itself — a `§99` section, a `§5.99` step past §5's eight, `authoritative: true`, a `derived_from` naming no file, a `source` citing nothing, and the extract deleted while §10 still requires it. Each produced its own distinct failure, and the unmutated tree stayed silent. `.claude/skills/README.md`'s cell said "23 checks" while the code had 24; the count is now removed from that cell rather than bumped, because a restated count is `RFC-756` by construction.

2026-08-30 (second entry, same day, correcting the first) — **Check 25's first version was
itself wrong**: register-only resolution fired on `F-W9-3-2`, a real, closed, correctly-cited
finding recorded only in its slice's closure record. Ruled by the lead: resolve against the
register, an archived phase register, OR a work-item closure record
(`docs/audit/work/*/README.md`, `docs/closures/INDEX.md#closure-recordsmd`) — never register-only.
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
`docs/research/` flagged several hundred false positives, every WK-661 and WK-664 task plan's own
locally-numbered "Findings" section among them. Second: `docs/roadmap.md` and
`docs/closures/CR-00709-phase-0-specification-status.md` are excluded from the scanned set even though both carry `(F..)`
tokens — a live check found `closures/CR-00709-phase-0-specification-status.md`'s `(F13)` citing
`docs/research/track-a-findings.md`'s own local F13, which collides with the register's
*unrelated* F13 and would have silently "resolved" against the wrong row rather than been
caught. A file citing its own locally-defined finding — by heading, ledger-table cell, or
bold paragraph lead-in — is exempt from the register check; the first two forms were
anticipated, the third (`docs/plans/PL-00846-wk-671-slice-1-evaluator-core-its-prerequisites-and-the-latency-harness.md`'s own four
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
exists), quoted once more in `docs/rulings/INDEX.md#2026-08-29-w11-slice1-rulingsmd`. Not resolved
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
questions — OQ-618, OQ-621, OQ-625, OQ-630 — and each got its consequence clause,
not just a status word: what deferring means for the platform (the bundle discount unpriced
and unmonitored; a challenger price never served; a `price_test` purpose the platform
refuses). The other eleven were bare rows the register had already decided or deferred
(OQ-541/553, OQ-557/558, OQ-622/623/624, OQ-627/628/629/631), repaired to carry their status
and either the consequence or a pointer to the register. The register itself was untouched
— it is the source of truth the check reads.

**Proven on deliberately broken input**: removing OQ-618's status token produced exactly
one targeted failure — `03-rating-engine.md:661: OQ-618 mirror row carries no status
token matching the register's 'deferred' status` — the summary line read `115 of 116`, and
the suite passed again on restore (`116 of 116`). Two design calls are recorded in the
script's docstring: mirror-side "resolved" / "determined" count as decided (OQ-638's row
says "DETERMINED"), and the row is read whole, because a decided row's question text can
contain a stray "open".

2026-08-22 — Re-confirmed while deciding OQ-571 and OQ-572. `audit-docs.py` passed
throughout (495 → 499 requirements, 76 → 78 open questions), and the gate-table snippet again
reported both ids under `missing` **before** the edit — the fourth time, and the same cause as
2026-08-19: questions raised inside WK-661 and mirrored correctly, but never placed on the plan. The
duplicate-id-in-prose trap above was found here, and it is the first failure mode where the two
snippets disagree with each other rather than with the roadmap.

2026-08-19 — Confirmed while recording OQ-565 (→ FR-55, FR-82). The script passed
before and after; the gate-table snippet reported `missing: ['OQ-565']` **before** the edit — a
question raised in WK-661 on 2026-08-18, correctly mirrored into the register, and never placed on the
plan, so the gate it belonged to had already closed by the time it was decided. That is the third
time the `missing` half has caught a question the plan could not see, and the first where the cost
was legible: an unplaced question is never scheduled, so it gets answered by whoever trips over it.
The count-recount snippet above was written here, because striking an id and leaving `12 (0 open)`
alone is the silent half of the same edit.

2026-08-18 — Confirmed while recording five maintainer decisions (OQ-577, OQ-576, OQ-584, OQ-585, OQ-639).
The script passed before and after; the **gate-table snippet did not**, and the two failures it
reported are written up above. Run the snippet at every raise *and* every decision — a decided
question still needs a row, because a row is where the revisit is scheduled.

2026-08-17 — Extended with **check 21**, the journeys' interface citations (FR-19(i)).
Proven on deliberately broken input in both halves — an undeclared endpoint and an undeclared
function each produced exactly one targeted failure, and the summary line's verdict flipped
with them. **It found a real defect on its first run**: WF-698 cited `profile_version()`, which
`01` §5.2 renamed to `profile_frame` / `profile_parquet` on 2026-08-15 without the journey
following.

Also worth knowing before the next check is added: **the number of checks is stated in
two places** — `.claude/skills/README.md` and `docs.yml`'s comment — and both have to be
edited. A third, this skill's own frontmatter, used to carry a bare count too, until the
2026-08-29 entry below removed it outright rather than keep bumping it — a bare figure
with no link to what keeps it current is the exact pattern that had already drifted three
ways twice. It used to be six places in total, until `CLAUDE.md`'s three mentions were
removed: §0's own rule is that counts which change do not belong in it.

2026-08-15 — Extended with checks 16–20 over `docs/notes/`. **All five were proven
against deliberately broken input**, twelve breakages in total, each producing exactly one
targeted failure and the suite passing again on revert: a removed `**Owner**` row, a status
of `pending`, a heading renumbered to the wrong number under filename `0001`, a duplicated
number, an index status disagreeing with its file, a note missing from the index, an index
row with no file, a dangling relative link, three deliberately-invalid ids, and a
requirement id written in the bold defining form. The wrong renumbering and the three
invalid ids, verbatim:

```
RFC-813 (wrong — the heading's real filename is 0001)
FR-PLAT-999
ADR-9999
NT-0042
```

*Fenced 2026-09-04 under RL-1044 §5.1's fence clause, extended to row (d): value
unchanged.*

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
and cannot be a position in a linear chain, which is now DEP-537.

The `$ref` check was likewise confirmed non-trivial by pointing a `$ref` at a non-existent
`$defs` fragment.
