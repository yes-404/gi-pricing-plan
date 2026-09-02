# Where Rulings 79 and 80 land, and the shape `plan-reviews.md` actually has, ruled (2026-09-02)

**What this is.** Two questions routed by the lead while W37-6 waits on a maintainer
go-ahead. The first is a commit-boundary question about work already in flight; the second is
the fourth and last of the discovery defects, the one no regex reaches. They are ruled below
as Rulings 81 and 82.

**Both were routed with figures that did not survive measurement, and in the second case the
figures were the question.** The brief reported `docs/audit/plan-reviews.md` as *15 `###`
headings, 12 records, three undated*. Executed against the file, it is **14 headings, 10
records, four unmatched** — and the fourth unmatched heading is a **filed §14 plan review**,
not a proposal. That changes what is being decided: the brief asked whether to widen a
pattern for three sub-headings, and the measurement says a governed review is being destroyed
alongside them. The corrections are set out in their own section below rather than folded
silently into the rulings, because the lead asked for verification against the artifacts and a
corrected count is the useful half of that answer.

**Neither ruling edits [`NT-0019`](../notes/0019-one-id-per-document.md) §1 or
[`docs/process/document-ids.md`](../process/document-ids.md).** Ruling 81 decides only a
sequencing question inside an already-ruled body of work. Ruling 82 decides an exclusion and a
unit boundary, and hands the positive family assignment to the planner on the Ruling 78
precedent rather than exercising a predicate once and trusting it.

## Authority

- **Ruling 81 is a sequencing decision inside an identified decision point** — Rulings 79 and
  80 assigned an owner and did not fix a commit boundary, and the boundary became live when
  the lead dispatched an executor against `main`. **Ruling 82 is a spec-versus-code conflict**:
  NT-0019 §4 step 2 says *"`plan-reviews.md` → one `CR-` per review"*, and the file contains a
  dated section that is not a review and is not sub-content of one, which the rule does not
  reach. [`.claude/roles/decision-maker.md`](../../.claude/roles/decision-maker.md) places
  both with this role; `CLAUDE.md` §0 requires the second be resolved rather than quietly
  reconciled.
- **The lead routed them here under the maintainer's delegation of 2026-09-01**, recorded at
  [`2026-09-01-maintainer-delegation-and-nt-0019-precedence.md`](2026-09-01-maintainer-delegation-and-nt-0019-precedence.md)
  §1, and neither falls in its §2 exclusions: neither is a fact only the maintainer holds,
  neither accepts a Work, Phase or Project close, and neither amends `CLAUDE.md`.
- **Every figure below is measured at `ffac8ba`**, which was `origin/main`'s tip when this
  record was written and still was when it was pushed (`git fetch origin && git rev-parse
  origin/main` re-run immediately before the commit). The branch is cut from that commit, so
  the measurement tree and the branch base are the same object — stated because the two came
  apart under a ruling record twice on 2026-09-01.
- **Re-read under [`delivery-process.md`](../process/delivery-process.md) §15 Rule 10** —
  *"a branch open when a ruling merges is re-read against that ruling before the branch itself
  merges."* No ruling merged during this branch's life; if one does, this record is re-read
  before it is merged.

## Acceptance Standard

**Why a ruling record carries this heading.** `audit-docs.py` check 28 classifies every dated
file in `docs/plans/` outside four suffixes as a plan needing this section, while
`check_plan_acceptance_standard`'s own docstring disclaims exactly that scope. That
disagreement is register finding F68 — see [`../audit/register.md`](../audit/register.md) —
carried forward with NT-0019's migration as its trigger. It is honoured here, and the check is
not patched from this branch.

1. `git grep -c '^## Ruling 81 —\|^## Ruling 82 —'` on this file returns `2`, and
   `git grep -n '^#\+ Ruling ' docs/plans/` shows 81–82 filling the gap immediately after
   Ruling 80 with no duplicate and no skip.
2. Each `### 2. Ruled` subsection names the chosen option **and every rejected option**, with
   the measured evidence that separated them.
3. Each ruling carries a `### 4.` section stating its acceptance as **a violation that must
   become detectable**, never as a description of correct behaviour — and each such violation
   is one an artifact can be edited to produce, not a human judgement.
4. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
5. `git diff --stat origin/main...docs/w37-rulings-81-82-boundary-and-plan-reviews` names
   exactly this one new file. No note, no template, no script, no test, no fixture, no
   workflow and no roadmap row is edited by this branch — every change these rulings oblige is
   work for a named owner.
6. Every claim about a script's behaviour below was produced by **executing that script**
   against the real artifacts, not by reading it; the probe and its output are quoted inline.

---

## Ruling 81 — the fix is inert on the real corpus, so the boundary is free; it lands on its own, and the reader and the writer land together

### 1. Verified first, at `ffac8ba`

**(a) The two symbols are in `doc-index.py`, and the leaf plan's one-commit list is about a
different file.** This is the load-bearing correction, because the brief's whole case for
landing inside W37-6 rested on the opposite.

```
$ grep -n '_ROW_FIELDS = \|def scan_phase_sections' scripts/doc-index.py
268:_ROW_FIELDS = frozenset(
353:def scan_phase_sections(path: Path) -> list[PhaseSection]:
```

[`2026-09-02-w37-6-migration-run-leaf-plan.md`](2026-09-02-w37-6-migration-run-leaf-plan.md)
§7.3 is titled *"Task 3 — `audit-docs.py`'s parsers, regexes and pins"* and its **Files:** line
reads `scripts/audit-docs.py`, `tests/test_audit_docs_*.py`. `doc-index.py` appears in that
plan's task list twice and neither is this: §7.6 (*"any path constant naming a pre-migration
directory"*) and §7.8 (`.github/workflows/docs.yml`'s `paths:`). The row and phase parsers are
in neither. And the plan predates the rulings entirely:

```
$ grep -c 'Ruling 79\|Ruling 80' docs/plans/2026-09-02-w37-6-migration-run-leaf-plan.md
0
```

**(b) The leaf plan's own simultaneity criterion does not capture this fix.** Its Goal states
what must be in the one commit: *"land in the same commit every instrument an author would
otherwise follow to produce a document the widened checks reject."* That is Ruling 66's
instrument set — the things that **teach an author a form**. `doc-index.py`'s row and phase
parsers are readers, not instruments; no author follows them to produce anything.

**(c) The leaf plan disclaims commit boundaries as a requirement, in its own words.** §7.5,
about the commit it most wants isolated: *"This is not a required commit boundary — Ruling 68
settles what (g) means, not how many commits the branch has before it is squashed."* A plan
that declines to make a boundary binding for `migrate`'s own output does not impose one on a
parser fix it never mentions.

**(d) NT-0019 §4's "one scripted PR, once" scopes to `migrate`, not to the parsers.** The
section head is *"Migration — one scripted PR, once"* and its body opens *"`scripts/doc-id.py
migrate`, deterministic and idempotent, run once and retained as evidence"*, followed by eight
numbered steps. A `doc-index.py` reader fix is none of the eight. The phrase binds the
migration run; it does not annex every file the migration will later exercise.

**(e) The decisive fact — the fix is inert on the real corpus, measured by execution.**

```
$ grep -c 'WK-\|SL-' docs/roadmap.md
0
$ grep -cE '^## (P[0-9]|Phase )' docs/roadmap.md
0
$ grep -c '```yaml' docs/roadmap.md
0
```

and the parsers themselves, imported and called against the real file:

```
scan_phase_sections(docs/roadmap.md) -> []
scan_roadmap_rows(docs/roadmap.md)   -> []
scan_bold_id_rows(docs/roadmap.md)   -> 0
```

The second group is stronger than the `grep`s above it and is why it was run.
`_parse_row_block` raises `HeaderError` on an unknown key **before** the `family in ("work",
"slice")` filter, so a fenced block under any `###`+ heading carrying a stray field would
raise rather than return `[]`. It returned `[]` with no exception. Three independent
conditions each make both parsers inert: the roadmap has no `WK-`/`SL-` token, no `## P<n>`
heading for `scan_phase_sections`'s `^##\s+(P\d+[a-z]?)\s+—` to match, and no fenced `yaml`
block at all for either to read.

**One of the two is not even reachable from the gate.** `audit-docs.py` loads `doc-index.py`
as `_doc_index` and calls `build_corpus` once, in check 39. `build_corpus`'s body calls
`scan_document_family`, `scan_roadmap_rows` and `scan_bold_id_rows` — **not**
`scan_phase_sections`, whose only caller anywhere is `phase_report` (`doc-index.py:812`),
reached from `doc-index.py`'s own `--phase` CLI flag and from tests. So Ruling 80's half
cannot change a gate result at `ffac8ba` by any path.

**(f) The CI step that consumes them is green and self-describes as pre-migration.**
`.github/workflows/docs.yml:43` runs `python3 scripts/doc-index.py --check`:

```
$ python3 scripts/doc-index.py --check
docs/INDEX.md does not exist and zero governed records were found under
.../docs — nothing to check yet (pre-migration)
$ echo $?
0
```

**(g) What the fix does break is contained in its own branch, and none of it is a governed
document.** The phase sections in `tests/fixtures/docs-ids/w37-3-corpus/roadmap.md` (`## P9`)
and `tests/fixtures/docs-ids/w37-4-rollup-raise/roadmap.md` (`## P6`) are written as fenced
` ```yaml ` blocks, which is the form Ruling 80 removes. `docs/_templates/PHASE.md` shows the
unfenced form and says so in its own comment: *"a phase section is plain fields under a
heading, exactly as shown below, not YAML front matter"*. So those two fixtures' **phase
sections** must be rewritten unfenced in the same branch or `phase_report`'s tests go red.
Their `###`/`####` **row** blocks stay fenced — §1.5 requires it (*"as a fenced block under the
row's heading"*), `scan_roadmap_rows`'s docstring repeats it, and Ruling 79 changes which
fields a row block may carry, not whether it is fenced.

### 2. Ruled

**The fix lands as its own pull request, merged on its own, before W37-6 runs. Reader and
writer land together in it.**

**Why the boundary is free rather than forced.** The sub-question the lead identified as
decisive is a fact, and (e) answers it: fixing `_ROW_FIELDS` and `scan_phase_sections` before
the migration creates **no red state on `main`**, because both parsers read nothing from the
real corpus today and will read nothing after the fix. There is no intermediate state to be
red in. A boundary is forced only when a fix cannot be made green without the migration's
output; every input this fix needs — the two row templates, `PHASE.md`, and the fixture
corpus — exists at `ffac8ba`.

**Why separately, once free.** Four reasons, in the order they bind:

1. **The argument for landing inside was a misattribution.** It rested on the leaf plan's
   one-commit list containing these parsers. It contains `audit-docs.py`'s (§1(a)), and the
   plan's own simultaneity criterion is about instruments an author follows (§1(b)). With that
   removed, nothing in NT-0019, the leaf plan, or Rulings 79 and 80 asks for simultaneity.
2. **W37-6 is gated on a maintainer go-ahead that has not been requested.** "Inside W37-6"
   is therefore not a date; it is "whenever the gate opens", and an unmerged fix rots against
   a moving `main` in the meantime.
3. **It makes the supervised run smaller and less confounded.** The leaf plan §4.4 treats the
   irreversibility of that commit as the thing the maintainer is being asked to accept. A
   migration run against an already-correct parser is one fewer variable in the run that can
   least afford one.
4. **Its acceptance tests are satisfiable today.** Both rulings' §4 items name positive
   controls that fail at `ffac8ba` — `unknown row field 'tree'`, and `PHASE.md`'s own body
   yielding no phase. A fix whose failing control exists before the migration does not need
   the migration to prove itself.

**Rejected: landing inside W37-6's commit.** Rejected on (a)–(d): no artifact requires it, and
the one that was cited names a different file.

**Rejected: landing the reader fix early and deferring the `doc-id.py` emitters to W37-6.**
This is the tempting middle, and it is the one shape that would create the red state the
brief was worried about. Ruling 79 §3 item 4 obliges `migrate`'s row emission to derive from
the same template, and Ruling 80 §3 item 4 obliges `_PHASE_TEMPLATE` to be re-emitted unfenced.
Fix the reader and leave the writer and `migrate` emits blocks its own reader rejects — a new
latent defect, of exactly the species Ruling 79 exists to remove, created by the act of
splitting. **The split is between the fix and the migration, never between the reader and the
writer.**

### 3. What it obliges

1. **The executor's in-flight branch merges on its own**, and carries both halves of each
   ruling: `scripts/doc-index.py` (the readers) **and** `scripts/doc-id.py` (`migrate`'s row
   emission at `:1576-1583` and `_PHASE_TEMPLATE` at `:1531-1541`, with the docstring at
   `:1552` replaced by a citation to Ruling 80, per that ruling's §3 item 4).
2. **The two fixtures' phase sections are rewritten unfenced in that same branch** —
   `w37-3-corpus/roadmap.md` and `w37-4-rollup-raise/roadmap.md`. Their row blocks are not
   touched. Any other fixture the branch's own test run reddens is treated the same way.
3. **"Owner: W37-6" in Rulings 79 and 80 §3 item 5 is not superseded and is not re-opened.**
   It assigned scope, and this ruling decides only the commit the scope's work rides in. If
   the branch does not merge before W37-6's go-ahead arrives, the work reverts to W37-6 with
   no further ruling needed.
4. **W37-6's leaf plan gains nothing from this.** No task is added to it, no acceptance item
   changes, and this record does not amend a filed plan (`CLAUDE.md` §12). Its §7.3 stays what
   it is: `audit-docs.py`'s parsers.
5. **The measurement carried forward from Rulings 79 and 80's *Not ruled* table stands** —
   whether check 30 reaches a `WK-`/`SL-` row block after `_ID_SCOPE_ROOTS` widens is still
   W37-6's executor's to establish, and landing this fix early neither answers it nor
   discharges it.

### 4. Acceptance — the violation that must become detectable

**The violation: `doc-id.py migrate` emits a row or phase block that `doc-index.py`'s own
parser will not read.** That is the state a split between reader and writer produces, and
nothing today reports it.

- **A round-trip check: take `migrate`'s emitted row block and phase section, feed each to
  `scan_roadmap_rows` and `scan_phase_sections`, and require the fields to survive.**
  *Violation: the writer's output is rejected, or silently mis-read, by the reader in the same
  repository.* This must be a test in the branch that lands the fix, not a task carried into
  W37-6 — it is the check that makes item 3's split-forbidding enforceable rather than
  advisory.
- **The two positive controls the rulings already name must be shown failing at `ffac8ba`
  before the fix, in the branch's own evidence** — `unknown row field 'tree'` from the row
  template's fenced block, and `PHASE.md`'s filled body yielding no phase. *Violation: a
  positive control that has never printed a failure.*
- **`python3 scripts/doc-index.py --check` and `python3 scripts/audit-docs.py` both exit 0 on
  the branch**, and the branch's `git diff --stat` against `origin/main` names no file under
  `docs/` other than a ledger. *Violation: a parser fix that edits a governed document.*

---

## Ruling 82 — the three undated headings are sub-content of one dated container section; no widening, and the container's family is the planner's to derive

### 1. Verified first, at `ffac8ba`

**(a) The heading census, and what the discovery function actually returns.**

```
$ grep -c '^### ' docs/audit/plan-reviews.md
14
```

and, importing `scripts/doc-id.py` and calling `_discover_plan_reviews(Path('.'))`:

```
RECORDS: 10
  2026-08-15  bodylines=  139  Plan review 2 — at W7b's close and before Phase 1a's exit demo
  2026-08-22  bodylines=  102  Plan review 3 — at W5's close
  2026-08-24  bodylines=  123  Plan review 4 — at W32's close
  2026-08-27  bodylines=  158  Plan review 5 — at W6b's close
  2026-08-27  bodylines=   32  Plan review 6 — at W7's close, before the Phase 1b exit demo
  2026-08-27  bodylines=  206  Plan review 7 — at W9's close
  2026-08-28  bodylines=  292  Plan review 8 — at W10's close
  2026-08-15  bodylines= 1094  Plan review 1 — at W6a's close
  2026-08-30  bodylines=  328  Plan review 10 — at W11's second close
  2026-08-31  bodylines=  332  Plan review 11 — completing the review sequence at W11's close
```

**Fourteen headings, ten records, four unmatched — not fifteen, twelve and three.** The
regex is `_REVIEW_HEADING_RE` (`scripts/doc-id.py:1196`):

```python
re.compile(r"^###\s+(.+?),\s*(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)
```

The four it does not match, with the reason:

| Line | Heading | Why unmatched |
|---|---|---|
| 1184 | `### Candidate A — do not move a branch someone is reading …` | no date |
| 1196 | `### Candidate B — declare up front that a count is not load-bearing …` | no date |
| 1218 | `### Also carried, and not a new rule` | no date |
| 1233 | `### Plan review 9 — at W11's close, 2026-08-30 — **FILED, with its drafting history intact**` | dated, but trailing text defeats the `\s*$` anchor |

**(b) The consequence, which is worse than a missing record.** `_discover_headed_split_file`
gives each match the text from its own start to the *next match's* start (`:1179-1181`), so an
unmatched heading is not a boundary at all — its text falls into the preceding record's body.
`Plan review 1` (line 1061, dated **2026-08-15**) therefore absorbs **source lines 1061–2155**:
its own body, the whole pending-proposals section, and the **entirety of Plan review 9**. The
`bodylines=` column above is `body.count("\n")`, and 1094 against 32–332 for every sibling is
the same span measured on the returned object rather than on the file. **A filed §14 plan
review, dated 2026-08-30, is silently destroyed as an independent record and re-dated fifteen
days earlier.** This is the same mechanism as the closure-record defect fixed in `#585`, and
it is the fourth heading — not the three the brief asked about — that causes it.

**(b1) The guard that exists for exactly this class cannot see it.** `migrate` passes these
drafts to `_check_legacy_file_not_silently_unrecognised` (`scripts/doc-id.py:1649-1677`),
whose own docstring says *"zero discovered records from it is unrecognised shape, full stop
… migrate refuses to guess and silently report success instead."* Its test is
`if drafts: return`. With ten drafts it returns at that line. **The guard is all-or-nothing:
it catches a pattern that matches nothing and is blind to one that matches most of a file** —
which is the state every one of these discovery defects has been in, including the roadmap
no-op and the closure-record split.

**(c) The three undated headings are sub-content, and the file says so in its own words.**
They are the only `###` headings under the file's **only** `##` heading, at line 1155:

```
## Pending proposals — for the §14 review at W11's close (drafted 2026-08-29)
```

whose first sentence is:

> **This is not a plan review and binds nothing.** It has no review number, no five questions
> and no maintainer acceptance line, because the §14 trigger — a workstream close — has not
> fired.

The three headings beneath it are two block-quoted rule proposals and one paragraph explaining
why a third is not a proposal (*"P13 sharpens rule 5 rather than adding to it … Nothing rides
with a rule-6 proposal"*). They carry no date because they were never run as a review.

**(d) They were consumed, and the container is cited by name.** Inside Plan review 9's body:

> **Candidates A and B, from the unnumbered "Pending proposals" section above, formally taken
> up**

and again in its sources list: *"Review 8 and the unnumbered 'Pending proposals' section, both
above in this document — read"*. So the section is not orphaned prose; it has inbound
citations from a governed record, and NT-0019 §4 step 6 rewrites every citation across the
tracked tree. Whatever the disposition, those two citations need a target that resolves.

**(e) A structural fact that no current check sees.** Because line 1155 is the file's only
`##`, Plan reviews **9, 10 and 11** are, by heading level, children of a section titled
*"Pending proposals"*. `_REVIEW_HEADING_RE` is anchored to `^###` and is blind to this, so it
changes nothing today — but any tool that walks heading structure rather than matching a flat
pattern will read three filed reviews as sub-content of a pending-proposals section.

### 2. Ruled

**Sub-content. The three undated headings are not records, and no widening of
`_REVIEW_HEADING_RE` may mint one for any of them. The unit that exists is the `##` section
they sit in, and its family assignment is handed to the planner.**

**Why sub-content is a finding rather than a judgement.** (c) and (d) settle it from the
document's own text: the container declares it is not a plan review, and Plan review 9 records
taking its contents up. Nothing was left to decide there — the brief asked a question whose
answer is written in the file.

**Rejected: widen the pattern to match undated `###` headings.** This mints three
`CR- kind: review` records for two block quotes and an explanatory paragraph. It is the mirror
of the closure-record defect exactly as the brief framed it, and it is also the error Ruling 77
corrected in the other direction: a governed document per heading, for things that are not
documents.

**Rejected: widen the pattern to `^##+` so the container itself becomes a `CR-`.** This mints
a closure record for a section whose own first sentence says it is not a review and binds
nothing. It is independently barred by NT-0019 §1.2: `CR`'s status subset is the single value
`active` and its `kind:` vocabulary is `work · phase · review`, none of which describes a set
of proposals that were superseded by being taken up. **This is the same ground on which Ruling
78 rejected `CR-` for the twelve non-close records**, and it is why the exclusion is ruled here
rather than left to the derivation.

**Rejected: leave the three inside their parent's body as the code currently does.** This is
the option the brief offered, and it does not survive (b). After the `$`-anchor is fixed, "the
parent" is `Plan review 1`, dated **2026-08-15** — fourteen days before the container was
drafted and fifteen before it was taken up. Folding a 2026-08-29 section into a 2026-08-15
record inverts the file's own chronology and buries a section that a later record cites twice
by name.

**Handed back, not ruled: which family and `kind:` the container takes.** Ruling 78's shape,
one day old and in this same Work: the decision-maker fixes the exclusion, the planner derives
the positive assignment against §5.2's full option set, and the derivation comes back to be
ruled. I have not enumerated that option set for this section, and assigning a family without
it is the *"predicate exercised once and trusted"* that
[`2026-09-02-w37-6-twelve-non-close-records-derivation.md`](2026-09-02-w37-6-twelve-non-close-records-derivation.md)
was written to prevent. Doing it here would be the same defect with a different author.

### 3. What it obliges

1. **`_REVIEW_HEADING_RE`'s `$` anchor is fixed so `Plan review 9` matches**, in the same
   shape `#585` used for `_CLOSURE_HEADING_RE` — a trailing-text capture group, not a looser
   date match. This is a code defect against merged W37-5, already tracked as the lead's task
   *"four discovery functions written against the fixture shape"*; (b) above is its measured
   blast radius and is the evidence that it destroys a record rather than merely missing one.
2. **The pattern is not widened to match an undated heading, at any heading level.** Whatever
   handles the container section handles it as a section, not as a fifteenth pattern match.
3. **The planner derives the container's family and `kind:`**, under NT-0019 §5.2 and §1.2,
   with four constraints established here and not re-derivable from the heading alone:
   - `CR-` is excluded, on §1.2's status subset and `kind:` vocabulary and on the section's own
     first sentence.
   - **The unit boundary is the `##` section — lines 1155–1232 — not the three `###` inside
     it**, and not a fold into `Plan review 1`.
   - Ruling 68 class 4's line-order constraint (*"the concatenation of every split output must
     reproduce this file's body lines in order"*) leaves exactly two placements: the section
     becomes its own record, or it becomes `Plan review 9`'s preamble by that record's
     boundary starting at 1155 instead of 1233. Both must be tested; a third is not available
     without reordering the file.
   - **Whichever is chosen, Plan review 9's two citations of *"the unnumbered 'Pending
     proposals' section above"* must resolve after the rewrite.** The preamble option makes
     that self-referential and the derivation must say what it rewrites to; that is a real
     cost of the option, not a disqualification of it.
4. **The mis-nesting in (e) is recorded, not fixed here.** Reviews 9–11 sitting under a `##`
   titled *"Pending proposals"* is a defect in `plan-reviews.md`'s own structure. It changes
   no output today. It goes to the lead as a finding, and the migration should not be the
   first thing to discover it.
5. **Nothing in this ruling is a task for W37-6's leaf plan**, and no filed plan is amended.

### 4. Acceptance — the violation that must become detectable

**The violation: a heading in a split source file becomes part of another record's body
without anything saying so.** Today that violation exists, four times in one file, and the
script reports success.

- **A coverage assertion over the split, run against the real file before the split is
  written out: every `#`, `##` and `###` heading in the source is either the heading of exactly
  one output record, or is listed by the script as a deliberate non-record with a reason.**
  *Violation: a heading that is neither, absorbed in silence.* This must fail at `ffac8ba`
  with four headings named — that is the positive control, and it is the check the per-heading
  model needed and did not have. `#585` fixed one file's symptom; this is the rule the symptom
  came from, and `_discover_closure_records` and `_discover_multi_ruling_files` are inside its
  scope, not only `_discover_plan_reviews`.
- **A record-count assertion with its own denominator: the split of `plan-reviews.md`
  produces eleven review records, and `Plan review 9` is one of them with its own date.**
  *Violation: a record whose body contains a second record's `###` heading.* That predicate is
  checkable on the output alone and would have caught this defect without anyone counting
  headings.
- **`_check_legacy_file_not_silently_unrecognised`'s test stops being `if drafts: return`.**
  It must compare what the file offered against what discovery took — headings seen versus
  records written, per split file — and refuse when they differ without a listed reason.
  *Violation: a partial match passing a guard written to catch a total one.* This is the
  generalisation the three fixed instances share and none of them closed: `scripts/doc-id.py:788-793`
  defines *"discovery finds nothing"* as *"already migrated"*, and the guard above narrows that
  to the all-or-nothing case only. A guard whose failing input is "zero records" has never been
  exercised by any of the four real defects, every one of which produced a positive count.

---

## Corrections to the brief that routed these

Filed rather than folded in, because the lead asked for verification against the artifacts and
because a corrected figure that arrives silently teaches nothing.

| Relayed | Measured at `ffac8ba` | Why it matters |
|---|---|---|
| *"`docs/audit/plan-reviews.md` has 15 `###` headings"* | **14** (`grep -c '^### '`) | — |
| *"`_discover_plan_reviews` produces 12 records"* | **10** (function executed) | — |
| *"Three carry no date at all"* | **Four** headings are unmatched; three carry no date, the fourth carries one with trailing text | The fourth is a filed §14 review, and it is the one that causes the damage. A brief scoped to the three would have fixed the harmless half |
| *"they … read as sub-content nested inside 'Plan review 9''s own section"* | They precede Plan review 9 (lines 1184–1232 against its heading at 1233) and are nested under a `##` at 1155 | The parent matters: it decides which record absorbs them, and the answer is `Plan review 1`, not review 9 |
| *"W37-6's leaf plan's 'what lands in this one commit' list includes `audit-docs.py`'s parsers and roots"* | **True, and it is a different file.** `_ROW_FIELDS` and `scan_phase_sections` are in `scripts/doc-index.py`; §7.3 names `scripts/audit-docs.py` | This was the entire case for landing inside W37-6 |

The first two figures are consistent with a count taken over `^##+ ` (14 `###` plus the one
`##` = 15) against a record count that assumed the `$`-anchor already fixed (11 reviews plus
the container = 12). That reconstruction is offered as the likely origin and is not itself
verified; what is verified is the measured column.

## Not ruled — and where each goes

| Item | Why not mine | Where it goes |
|---|---|---|
| **The container section's family and `kind:`** | Ruling 78's precedent: the exclusion is the decision-maker's, the positive assignment is derived by the planner against §5.2's full option set and ruled afterwards. I have not done that enumeration | **The planner**, with Ruling 82 §3 item 3's four constraints. Comes back here to be ruled |
| **The `$`-anchor fix in `_REVIEW_HEADING_RE`** | A code defect in merged W37-5, not a spec-versus-code conflict — the same species as the closure-record split already fixed in `#585` | **The lead**, folded into the existing task for the four discovery functions. §1(b) supplies the blast radius it did not have |
| **`plan-reviews.md`'s heading mis-nesting (§1(e))** | A structural defect in a governed document, not a decision about what the standard means | **The lead**, as a finding. Fixing it before the migration is cheaper than after, but it blocks nothing |
| **Whether the executor's branch merges before or after any other open PR** | Merge order is the lead's, and `CLAUDE.md`'s standing rule reserves every merge to it. Ruling 81 fixes that the branch merges *on its own*, not when | **The lead** |

## Provenance

Routed by the lead on 2026-09-02 under the 2026-09-01 delegation, alongside an explicit
invitation to decline either question. Neither was declined; the second was ruled narrower
than it was asked, and the narrowing is stated in Ruling 82 §2 rather than left as silence.
Both rulings were written against `ffac8ba` with every script claim produced by executing the
script.
