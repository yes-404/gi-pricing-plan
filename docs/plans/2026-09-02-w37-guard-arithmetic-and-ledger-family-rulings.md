# The split guard's arithmetic, and the family the ten W5 slice records take, ruled (2026-09-02)

**What this is.** Two questions the maintainer asked for as rulings, routed by the lead on
2026-09-02. The first is a design question stated as a property with the design left open; the
second is a family assignment [Ruling 78](2026-09-02-w37-6-leaf-plan-findings-rulings.md)
reserved and the planner's derivation handed back. They are ruled below as Rulings 83 and 84.

**Ruling 83's short answer is that `#585`'s approach does not generalise, and the reason is
structural rather than a matter of effort.** `#585` did something better than it is usually
credited with: its loop has no silent-skip branch, so every match is classified or raises, and
the corpus supplies its own count with nothing maintained alongside it. What that cannot reach
is the gap between the **match set** and the **unit set**, because **the denominator is still
the matcher itself** — a census counted with the pattern you split with closes trivially and
proves nothing. Measured live: `_RULING_HEADING_RE` misses **six** ruling headings across the
corpus, three of them for a reason no widening would have been aimed at, and no count taken
with that regex can ever say so.

**The other half of the answer is already in the repository.** `_check_roadmap_not_silently_unrecognised`
reads a *post-migration marker* instead of asking the legacy matcher — an independent
denominator, exactly this ruling's principle, implemented once for one file. It is binary, so
one `WK-` row silences it. `#585` has the arithmetic and no independent denominator; the
roadmap guard has the independent denominator and no arithmetic. **The ruling is both halves,
and neither is new.**

**Ruling 84's short answer is that the obstacle is already gone.** The planner's derivation
rejected `LG-` on one measured ground — that `slice:` is required and unsatisfiable — and that
ground was refuted in
[`2026-09-02-w37-template-parser-conflicts-rulings.md`](2026-09-02-w37-template-parser-conflicts-rulings.md)'s
closing section without a ruling number being minted, because a refuted premise decides
nothing on its own. What it left undecided is the adoption, which Ruling 78 and the derivation
both reserved here. That is what Ruling 84 does, in a form one step smaller than the
derivation's own recommendation.

**Rulings 81 and 82 are the sibling record filed earlier the same day**, merged as `0e9f620`
(PR #589) while this branch was open. 83 and 84 continue the sequence with no gap.

## Authority

- **Both were routed by the lead under the maintainer's delegation of 2026-09-01**, recorded at
  [`2026-09-01-maintainer-delegation-and-nt-0019-precedence.md`](2026-09-01-maintainer-delegation-and-nt-0019-precedence.md)
  §1, and neither falls in its §2 exclusions: neither is a fact only the maintainer holds,
  neither accepts a Work, Phase or Project close, and neither amends `CLAUDE.md`.
- **Ruling 83 was asked for as a ruling in the maintainer's own words**, relayed by the lead:
  *"'Found nothing means already migrated' was a fixture-corpus assumption; the real tree needs
  the arithmetic to close. How — options, trade-offs, a recommendation — is a ruling to bring
  me, not something to pick silently."* The property is the maintainer's; the design is what is
  ruled here.
- **Ruling 84 is the decision Ruling 78 and the derivation both reserved.**
  [`2026-09-02-w37-6-twelve-non-close-records-derivation.md`](2026-09-02-w37-6-twelve-non-close-records-derivation.md)
  §3.3 ends *"Recommendation (e), decision to the decision-maker"*, and the maintainer's
  instruction is that it be settled before the run rather than discovered during it: *"That is
  a decision, not a code change — route it as one, so a run is not halted on it on the day."*
- **Every figure below is measured at `ffac8ba`**, `origin/main`'s tip when this record was
  written and the commit this branch was first cut from. **`origin/main` then advanced to
  `59bba94` while the branch was open, and this branch is rebased onto it** — stated rather
  than smoothed over. The two commits are PR #589 (this record's own sibling) and PR #590 (the
  withheld go-ahead, plus a roadmap-row figure correction). `git diff --name-only ffac8ba
  59bba94` lists three files — two new records under `docs/plans/` and `docs/roadmap.md`,
  changed by one line. Nothing under `scripts/`, `docs/_templates/` or `docs/notes/` moved, and
  §1(g)'s two roadmap counts re-measure to the same **41** and **30** at `59bba94`, so every
  citation below holds at both trees. **The measurement tree stays `ffac8ba`** — that is a
  fixed fact; which commit is `main`'s tip is not, and is why it is not restated as one below.
- **Re-read under [`delivery-process.md`](../process/delivery-process.md) §15 Rule 10** —
  *"a branch open when a ruling merges is re-read against that ruling before the branch itself
  merges."* Rulings 81 and 82 merged during this branch's life and the re-read was done: Ruling
  81's commit-boundary reasoning is applied by Ruling 83 §2 and its citation updated from an
  open PR to the merged record; Ruling 82's plan-reviews measurement is cited in §1(d); neither
  changes a conclusion here. PR #590 corrects the roadmap row's plan-reviews figures to the same
  values and attributes them to *"a report"* — the section below names what that report was
  quoting, which is the one thing it does not carry.
- **Neither ruling edits [`NT-0019`](../notes/0019-one-id-per-document.md) §1,
  [`document-ids.md`](../process/document-ids.md), or any template.** Ruling 84 in particular
  needs no template edit, which is the respect in which it is smaller than the recommendation
  it adopts.
- **No filed plan is amended.** W37-6's leaf plan is frozen at its date; the two obligations
  these rulings put on that slice are stated here and are a new dated artifact, not an edit.

## Acceptance Standard

**Why a ruling record carries this heading.** `audit-docs.py` check 28 classifies every dated
file in `docs/plans/` outside four suffixes as a plan needing this section, while
`check_plan_acceptance_standard`'s own docstring disclaims exactly that scope. That
disagreement is register finding F68 — see [`../audit/register.md`](../audit/register.md) —
carried forward with NT-0019's migration as its trigger. It is honoured here, and the check is
not patched from this branch.

1. `git grep -n '^#\+ Ruling ' docs/plans/` shows 83–84 filling the gap immediately after
   82 with no duplicate and no skip, counting 81 and 82, merged as `0e9f620`.
2. Each `### 2. Ruled` subsection names the chosen option **and every rejected option**, with
   the measured evidence that separated them. Ruling 83 additionally carries the maintainer's
   requested *options, trade-offs and a recommendation* as a table, so the rejected designs are
   readable without reconstructing them.
3. Each ruling carries a `### 4.` section stating its acceptance as **a violation that must
   become detectable**, never as a description of correct behaviour, and each such violation is
   one an artifact can be edited to produce.
4. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
5. `git diff --stat origin/main...docs/w37-rulings-83-84-guard-arithmetic-and-ledger-family`
   names exactly this one new file. No note, no template, no script, no test, no fixture and no
   roadmap row is edited by this branch.
6. Every claim about a script's behaviour below was produced by **executing that script** or by
   reading the shipped source at `ffac8ba`, never from a report; each probe and its output is
   quoted inline, and where a figure came from a relay it is marked as such and re-measured.

---

## Ruling 83 — the census must not be counted with the splitter's own pattern; `#585`'s shape does not generalise, and a matcher-derived denominator is why

### 1. Verified first, at `ffac8ba`

**(a) What the guard does today.** `_check_legacy_file_not_silently_unrecognised`
(`scripts/doc-id.py:1649-1677`) is wired at three call sites — `:1829` closure-records,
**`:1834` plan-reviews**, `:1842` register. Its docstring states the intent — *"zero discovered
records from it is unrecognised shape, full stop"* — and the error it raises states the
consequence: *"this script's legacy pattern does not match this file's real shape … migrate
refuses to guess and silently report success instead."* Its whole test is:

```python
if drafts:
    return  # discovery found something; nothing ambiguous to flag
```

**It trips on zero and on nothing else.** Against `plan-reviews.md` it receives ten drafts for
eleven reviews and returns at that line. The maintainer's characterisation is exactly right:
this is a fixture-corpus assumption, because in a fixture every heading matches by
construction, so "found something" and "found everything" are the same observation.

**(b) What `#585` actually changed, read from the shipped source rather than from its title.**
`_discover_closure_records` (`:1211-1263`) does **not** take a census. It:

1. finds headings with `_CLOSURE_HEADING_RE` (`:1193-1195`), which `#585` widened to
   `^###\s+(.+?),?\s*(?:accepted\s+)?(\d{4}-\d{2}-\d{2})(.*)$` — a trailing-text capture group
   the review regex still lacks;
2. classifies each match by title prefix (`_CLOSURE_AUDIT_TITLE_PREFIXES`) or by a
   `"not closed"` trailer;
3. **raises** `NotImplementedError` on an unclassifiable match.

**The property it achieves is worth naming exactly, because it is real and it is not the one
needed.** The loop body has no `continue`, no `pass` and no silent-skip branch: every iteration
either raises or appends. So **every match is accounted for** — exhaustiveness over the match
set, enforced by control flow rather than by a count, which is a better mechanism than any
assertion would have been. What it cannot reach is the difference between the **match set** and
the **unit set**. Its denominator is `_CLOSURE_HEADING_RE`'s own match count: a closure heading
at `##`, or one carrying no date, is not an unclassified match but a *non-match*, and no
exhaustiveness property over matches can see it. The PR title's *"21 headings, 11 classified,
10"* describes the outcome on today's corpus; no line of code computes the 21 independently.

**And the raise currently masks the guard entirely for that file.** Executed against the real
tree, `_discover_closure_records` does not return eleven drafts — it raises at match index 11:

```
NotImplementedError: migrate: …/docs/audit/closure-records.md, heading
'W5 — the GLM spine' (2026-08-15) is not yet closed -- migrate cannot assign a
family a governed document does not have (task #31).
```

`migrate` calls it at `:1828` inside no `try`, so control never reaches the guard at
`:1829-1831`. That guard is unreachable for closure-records on today's tree, and its blind spot
there is hidden rather than absent — it will surface the moment Ruling 84 replaces the raise.

**(c) The measurement that settles whether it generalises.** `_RULING_HEADING_RE` (`:1091`) is
`^##\s+Ruling\s+(\d+)\s*(?:—\s*(.+))?$`. Across `docs/plans/` at `ffac8ba`:

```
$ git grep -c '^## Ruling '  -- 'docs/plans/*.md'   (summed)   77
$ git grep -c '^# Ruling '   -- 'docs/plans/*.md'   (summed)    3
$ git grep -c '^### Ruling ' -- 'docs/plans/*.md'   (summed)    3
```

**Six ruling headings are invisible to the splitter, and they fail for two different reasons.**
The three `#` (h1) fail on heading level alone:

```
docs/plans/2026-09-01-nt-0016-slice2-fr-data-32-ruling.md:1:# Ruling 59 — …
docs/plans/2026-09-01-ruling-60-census-provenance-checkout-depth.md:1:# Ruling 60 — …
docs/plans/2026-09-01-ruling-61-notes-tombstone-stubs-watched.md:1:# Ruling 61 — …
```

The three `###` fail on **both** level and id form — their ids are letter-suffixed, and
`(\d+)` cannot match them:

```
docs/plans/2026-08-30-nt-0012-0013-0014-adoption.md:67:### Ruling A1 — …
docs/plans/2026-08-30-nt-0012-0013-0014-adoption.md:81:### Ruling A2 — …
docs/plans/2026-08-30-nt-0012-0013-0014-adoption.md:96:### Ruling A3 — …
```

**W37-6's leaf plan §7.5 reports the first three and not the second three** — *"There are 72
ruling headings across 29 files, of which 3 are `#` (h1), not `##`"*. Re-measured here as 83
across 32 files, the growth being rulings filed since. The h1 shape was found by someone
counting headings by hand; the letter-id shape was not found at all, because **there is no
count under which it is missing** — every count anyone has run was taken with a pattern that
requires a number.

**(d) The class, enumerated.** Every `_discover_*` function derives its denominator from its own
matcher; none takes an independent census.

| Function | Line | Matcher | Its blind spot, where one is known |
|---|---|---|---|
| `_discover_notes` | 1002 | `_NOTE_TITLE_RE` | requires a 4-digit id and an em dash |
| `_discover_adrs` | 1050 | `_ADR_TITLE_RE` | as above |
| `_discover_multi_ruling_files` | 1109 | `_RULING_HEADING_RE` | **6 headings**, per (c) |
| `_discover_closure_records` | 1211 | `_CLOSURE_HEADING_RE` | widened by `#585`; still `###` + a date |
| `_discover_plan_reviews` | 1265 | `_REVIEW_HEADING_RE` | **4 headings**, one of them a filed review (Ruling 82) |
| `_discover_plain_plans` | 1274 | `_PLAN_FILENAME_RE` | filename-shaped, not heading-shaped |
| `_discover_requirements` | 1311 | `_LEGACY_SPEC_BOLD_RE` | — |
| `_discover_roadmap` | 1378 | three legacy REs | **all three match zero**; no longer silent — see §1(e) |
| `_discover_register` | 1428 | `_REGISTER_FINDING_RE` | unit is a table cell, not a heading |

Four of the nine have a measured, live blind spot today. The register's unit is a row rather
than a heading, which matters for how the property below is worded and not for whether it
applies.

**(e) The four guarded files, each function and each guard called directly at `ffac8ba`.**
Every cell below is an execution, not a reading:

| Function | Result | Guard | Guard result |
|---|---|---|---|
| `_discover_roadmap` | `0` drafts | `_check_roadmap_not_silently_unrecognised` (`:1864`) | **raises** |
| `_discover_register` | `0` drafts | `_check_legacy_file_not_silently_unrecognised` (`:1842`) | **raises** |
| `_discover_closure_records` | **raises** at match index 11 | (`:1829`) | **never reached** |
| `_discover_plan_reviews` | `10` drafts for 11 reviews | (`:1834`) | **silent** |

**Two corrections to the shape this is usually described in.** First, `_discover_closure_records`
is commonly reported as *"21 headings → 21, fixed by `#585`"*. It does not produce 21 on this
tree; it raises, and its guard is dead code behind that raise (§1(b)). `#585` fixed the
*classifier*, and the arithmetic line describing the result is a description of the
post-Ruling-84 state, not the current one. Second, the roadmap's *"silent no-op"* is no longer
silent: task #32's guard landed and fires. What remains there is a different question, below.

**(f) The principle this ruling adopts is already implemented once, in this repository, for one
file.** `_check_roadmap_not_silently_unrecognised` (`:1605-1647`) does not ask
`_discover_roadmap` how many works it found. It asks whether `docs/roadmap.md` carries any
`WK-` row, read with `_ROADMAP_ROW_RE` — **a pattern that encodes the post-migration marker
rather than the legacy matcher's expectations.** Its docstring states exactly why: *"a roadmap
that still has works described in a shape `_discover_roadmap`'s legacy patterns do not
recognise looks identical, to this script, to a roadmap with nothing left to convert."* That is
this ruling's principle, and the recommendation below generalises an existing local solution
rather than importing a new idea.

**Its limitation is equally instructive, and is why the principle alone is not the ruling.** The
check is binary — `if any(prefix == "WK" ...): return`. **One** `WK-` row silences it. It has an
independent denominator and no arithmetic, so it detects a total failure and not an undercount
— the mirror of `#585`, which has an arithmetic over its matches and no independent
denominator. **Neither half is sufficient and the ruling is both.**

**(g) A figure worth pinning, because two correct counts of it disagree.** `docs/roadmap.md`
carries **41** distinct bolded work ids and **30** works that are a leading table row:

```
$ grep -oE '\*\*W[0-9]+[a-z]?\*\*' docs/roadmap.md | sort -u | wc -l   → 41
$ grep -cE '^\| \*\*W[0-9]+[a-z]?\*\*' docs/roadmap.md                 → 30
```

Both are right over different corpora; the eleven-item difference is bolded work tokens that
are not row heads. §4 step 3 says *"each Work a `WK-` row"*, so **which of the two is the
conversion population is an open question**, not a discrepancy to reconcile away — and it is
precisely the kind of question a census surfaces and a matcher-derived count cannot.

### 2. Ruled

**The guard's predicate becomes an arithmetic that closes, and the denominator is derived
independently of the splitter's own matcher.**

For every source a `_discover_*` function splits, `migrate` must account for **every unit the
source offers**, counted by a pattern that does not encode the splitter's expectations:

- for a heading-split file, every heading at any level — `^#{1,6}\s`;
- for a row-split file, every candidate row of the table being read.

Each unit is classified into exactly one of three buckets, and the totals must balance:

1. **a record** — it heads exactly one output draft;
2. **body** — it sits below the split's own level, or is the file's own title folding into the
   preamble. **Derived, not listed**;
3. **a declared exception** — named, with a reason, in code.

**If the three do not sum to the total, `migrate` refuses and names the specific units, not a
count.** A count says something is wrong; the units say what.

**Options, trade-offs, and why this one.** The maintainer asked for these to be readable rather
than reconstructed.

| # | Design | Assessment |
|---|---|---|
| (a) | **Expected-count constant per call site** — `assert len(drafts) == 11` | **Rejected.** A transcribed count, stale on the next filed review, and it cannot name which unit was lost. It is the defect class Ruling 70 struck `_ROW_FIELDS` for, re-created in the guard that exists to catch it |
| (b) | **`#585`'s shape, generalised** — widen each matcher, classify every match, raise on the unclassifiable | **Rejected as sufficient, adopted as necessary.** It is the right treatment for a *known* variation and it is why closure-records is now correct. It cannot close the arithmetic, because its denominator is the widened matcher: (c)'s letter-id headings are invisible to any count taken this way, and widening again only moves the boundary |
| (c) | **Maintained exclusion list per file** — an explicit table of headings that are deliberately not records | **Rejected as the primary mechanism, kept as bucket 3.** It closes the arithmetic, but the list is itself a transcribed policy with the same staleness failure as (a). Acceptable only for what cannot be derived, and only with a reason per entry |
| (d) | **Structural invariant, no list** — no output record's body may contain a heading at the split's own level | **Adopted, as the derivation behind bucket 2.** Needs nothing maintained and would have caught Plan review 9 immediately, since Plan review 1's body contains four `###` headings. Alone it is not enough: it says a record swallowed something, not that a source unit went unaccounted for |
| (e) | **(d) plus a level-independent census, buckets 1–3 balancing** | **Recommended and ruled.** The census is the only term that cannot be gamed by widening a regex, and the only one that surfaces a unit whose *id form* — not its position — is unexpected. It is not a new idea here: §1(f)'s roadmap guard already reads a post-migration marker instead of asking the legacy matcher, and this generalises that to an arithmetic instead of a yes/no |

**Why the denominator is the whole ruling.** Every previous fix in this class widened a
matcher. Each was correct and each left the same hole, because the thing measuring coverage
and the thing providing it were the same expression. Ruling 70 struck `_ROW_FIELDS` for
transcribing a policy the templates already declared; this is the same principle turned on the
guard: **a check may not derive its own denominator from the thing it is checking.**

**Rejected: leaving the guard as it is and relying on Ruling 68 acceptance (g) class 4.** Class
4 requires *"the concatenation of the outputs reproduces the input's body lines in order"*. Every
defect in this class **passes** it — the lines are all present, in order, in the wrong record.
W37-6's leaf plan §7.5 already says so in its own words: *"A dropped section is caught; a
misattributed one is not."* Class 4 cannot be the arithmetic.

**Rejected: deferring this to W37-6.** The guard fix is testable today against a corpus that
already produces four distinct violations, and W37-6's go-ahead is withheld. This follows
Ruling 81's reasoning and differs from it in one respect that is stated rather than
smoothed: this change **does** alter behaviour on the real tree — `migrate` will raise where it
now succeeds. That is not a red gate, because `migrate` is not run by CI and the tests exercise
`tests/fixtures/docs-migration`, not the real corpus. It is the intended effect.

### 3. What it obliges

1. **The census runs before W37-6, not during it.** Every unclassified unit is resolved and
   recorded ahead of the go-ahead. This is the maintainer's instruction on Ruling 84 —
   *"so a run is not halted on it on the day"* — applied to the same mechanism: a guard that
   halts loudly is only an improvement if what it halts on has already been cleared.
2. **The six ruling headings of §1(c) get a disposition each.** The three h1 files are one
   ruling per file and need no split; the three `Ruling A1`–`A3` carry an id form
   `_RULING_HEADING_RE` cannot express, and whether they are rulings, sub-content, or a
   legacy form to be renumbered is **not decided here** — see *Not ruled*.
3. **Bucket 2 is derived and bucket 3 is declared.** A heading below the split level is body by
   computation; anything in bucket 3 carries a reason string in code, and a bucket-3 entry that
   could have been derived is a defect in the fix rather than in the corpus.
4. **The guard's message names units, never counts.** The failure text lists the file and each
   unaccounted heading with its line number.
5. **`#585`'s classification stays.** Nothing here reverts it; it becomes bucket 1's
   classifier, under a denominator it no longer supplies.

### 4. Acceptance — the violation that must become detectable

**The violation: a source unit exists that heads no record, is not derivably body, and is named
in no declared exception — and `migrate` completes.** Today that violation exists at least ten
times across three files and `migrate` reports success.

- **The census fails at `ffac8ba` naming the four `plan-reviews.md` headings and the six ruling
  headings of §1(c), by file and line.** That is the positive control, and it must be shown
  failing before the fix. *Violation: a guard that has never printed a failure.*
- **A mutation the widening approach cannot survive: add a heading to a split source whose id
  form the splitter's regex cannot express** — the `Ruling A1` shape, in a fixture. The census
  must red. *Violation: the guard's verdict is unchanged by a unit it cannot parse* — the
  signature of a denominator taken from the matcher, and the one test (b) fails and (e) passes.
- **A second mutation, in the opposite direction: delete a declared exception's reason string.**
  The guard must refuse rather than silently treat the entry as derived. *Violation: bucket 3
  accepting an unexplained entry.*
- **`_check_legacy_file_not_silently_unrecognised`'s `if drafts: return` is gone**, and a
  ten-of-eleven discovery on `plan-reviews.md` reds. *Violation: a partial match passing a
  guard written to catch a total one.*
- **The roadmap guard stops being satisfied by a single `WK-` row.** A fixture roadmap carrying
  41 works and exactly one `WK-` row must red. *Violation: an independent denominator used as
  a yes/no rather than as an arithmetic* — §1(f)'s limitation, and the half `#585` has that the
  roadmap guard lacks, exactly as the roadmap guard has the half `#585` lacks.

---

## Ruling 84 — the ten W5 slice records become `LG-`, carrying `work:` and no `slice:`; no template edit is needed

### 1. Verified first, at `ffac8ba`

**(a) What the ten are.** Rows 12–21 of the derivation's 21-row enumeration, all in
`docs/audit/closure-records.md`, all headed `W5 — <slice>, 2026-08-1{5,6,7} *(in progress, not
closed)*`. The derivation establishes they are per-slice delivery records, quoting row 12's own
closing paragraph: *"**W5 is not closed and this is not a closure record.** It is one slice of …
requirements, written down so the next one starts from what is true."* The *"in progress, not
closed"* qualifier describes **W5's state when each record was written**, not the slice's: row
5 of the same file is `W5 — Modelling: closed 2026-08-22`, and `docs/roadmap.md:232` carries
`| **W5** | Modelling workbench … | ✔ **closed 2026-08-22** |`.

**(b) `_discover_closure_records` raises on them today**, which is the correct behaviour and
the reason this is a decision rather than a code change (`scripts/doc-id.py:1240-1245`):

```python
if "not closed" in trailer.lower():
    raise NotImplementedError(
        f"migrate: {path}, heading {title!r} ({date_str}) is not yet closed -- "
        f"migrate cannot assign a family a governed document does not have (task "
        f"#31). Resolve the record's disposition (or close it) before migrating."
    )
```

**(c) The derivation's sole ground for rejecting `LG-` is false, and I re-measured it rather
than taking the refutation's word.** §3.2 argued that `docs/_templates/LG.md` declares
`slice: SL-NNNNN` unconditionally, making it **required** under Ruling 70, with no `SL-` row
in existence to name. Executing `derive_field_policies()` against the real templates:

```
ledger permitted: corrected_by created family id owner phase plans relates
                  slice status title tree work
ledger required : created family id owner status title
  'slice': permitted=True  REQUIRED=False
  'work' : permitted=True  REQUIRED=False
```

Ruling 70 governs the **permitted** set. Required-ness is a separate mechanism —
`required = frozenset(_CORE_HEADER_FIELDS) & permitted`, plus `{"id"}` — and `slice:` is not a
core field. **A ledger with no `slice:` passes check 30.**

**(d) A second, independent ground the refutation did not use: the template says so itself.**
`docs/_templates/LG.md`'s own comment block instructs *"delete this comment block, and **remove
any field this ledger does not use**."* Omitting `slice:` is not a tolerated gap; it is the
documented way to use the template.

**(e) The §1.7 residual — the derivation's stated reason for not taking its own
recommendation — corrected, and then answered.** The refutation wrote that §1.7 *"routes the
terminal row through either axis — 'a `CR-` cites the plan's `slice:`/`work:`'"*. **That
quotation drops a conjunct.** §1.7's table reads, for the terminal row:

| `closed` | a `CR-` cites the plan's `slice:`/`work:` **and the `SL-` row is `closed`** |

With no `SL-` row, that row cannot be reached. The refutation's conclusion survives, but not
by the route it gave, so the real answer is recorded here:

- **`execution` is a property of a `PL-`, never of an `LG-`.** §1.7: *"`doc-index.py` derives it
  into an `execution` column"* for a plan. A ledger has no execution column to lose.
- **No `PL-` routes through any of the ten.** The earliest filed plan is
  `docs/plans/2026-08-18-profile-contract.md`; the ten are dated 2026-08-15 to 2026-08-17 and
  predate the convention. `grep -rl` across `docs/plans/` for their headings returns only the
  derivation itself. Their `plans:` is empty, so no plan's column is computed through them.
- The 16 existing `-ledger.md` files are in the identical position and carry no front matter at
  all today.

**(f) `work:` resolves.** `docs/roadmap.md` carries 30 bolded work rows and **zero** per-slice
rows, W5's among the 30. W37-6 converts works to `WK-` rows in the same commit that creates
these ledgers, so `work:` names a row that exists post-migration. `slice:` would name nothing,
which is the reason to omit it rather than a reason to invent a row.

### 2. Ruled

**All ten become `LG-`, `family: ledger`, in `docs/ledgers/`, carrying `work:` set to W5's
post-migration `WK-` id and **no** `slice:` field. `docs/_templates/LG.md` is not edited.**

This is the derivation's recommendation (e) **minus its template edit**, which §1(c) and §1(d)
show to be unnecessary. Recording the difference matters: (e) proposed *"`slice:` made
conditional in `docs/_templates/LG.md`"*, and adopting it as written would edit a template to
license something the template already licenses — a change to §1's surface for no gain, which
Ruling 70 held goes back to the maintainer.

- **`status:`** is `LG`'s own vocabulary, `active → closed`, and §1.6 gives it to the auditor
  *"at slice close"*. W5 closed 2026-08-22, so the expected value is `closed` — but each of the
  ten is read for its own outcome rather than blanket-stamped, and any that records a slice
  that did not complete takes `retired` with the reason in its body. **Ten reads, not one
  assumption.**
- **`owner:`** is `executor`, per §1.6's `LG` row and the template's own default.
- **`created:`** is each record's own date, per NT-0019 §4 step 1.
- **`phase:`** is W5's phase, derived at migration time.

**Rejected: (a), `LG-` with `SL-` rows minted retroactively.** The derivation rejected it and
the refutation independently closed it: *"Minting `SL-` rows out of the map plan's slice table
would be creating governed rows rather than converting them — outside §4's 'one scripted PR,
once' over existing things."* §1.6 also makes `SL` the planner's, cut in a map plan; W5 had none.

**Rejected: (b) `RS-`.** Wrong unit — these are delivery records, and row 12 distinguishes
itself from the audit shape in its own text.

**Rejected: (c) `CR-`.** Ruling 78 already, and independently §1.2: `CR`'s status subset is the
single value `active` and its unit is *"one work, phase or review close"*. These are not closes.

**Rejected: (d) consolidation into one document.** Destroys the per-slice unit that is the only
record of ten slices, and matches no §5.2 rule.

**Rejected: leaving them `UNDETERMINED` until the run.** This is what the maintainer's
instruction forecloses, and §1(b) shows the cost — `migrate` raises on the first of the ten, so
the run stops at a decision nobody is positioned to take on the day.

### 3. What it obliges

1. **`_discover_closure_records`'s `"not closed"` branch stops raising and emits an `LG-`
   draft** with the fields of §2. The raise was correct while the family was undecided and is
   wrong the moment it is decided; it is replaced, not deleted, by the classification.
2. **The ten join the 16 existing `-ledger.md` files in `docs/ledgers/`**, which §5.2 already
   routes there. `docs/ledgers/` does not exist at `ffac8ba` and is created by the migration.
3. **No `SL-` row is minted for any of them**, and their absence is not a defect to fix in the
   standard: §4 step 3 converts slices that exist in the roadmap and there are none in any
   shape, so the clause is vacuous rather than unsatisfiable.
4. **Rows 12–21 of the derivation's §1 table move from `UNDETERMINED` to this ruling.** The
   derivation is frozen at its date and is not edited; this record is its resolver, and the
   derivation's Acceptance Standard item 4 — which makes materialising them early a detectable
   violation — is discharged by that resolution rather than by an edit.
5. **`slice:` stays permitted for every other ledger.** Nothing here narrows the field; a
   ledger cut from a map plan carries it as the template shows.
6. **Ruling 83's census lands with this or before it, never after.** Ruling 83 §1(b) shows the
   guard at `:1829-1831` is unreachable for `closure-records.md` today, because the raise this
   ruling removes pre-empts it. Removing the raise on its own therefore does not restore a
   working guard — it exposes one whose blind spot has simply been hidden. The two changes are
   ordered, and this is the ordering.

### 4. Acceptance — the violation that must become detectable

**The violation: one of the ten materialises as anything other than an `LG-` in
`docs/ledgers/`, or carries a `slice:` naming a row that does not exist.**

- **A test that runs `_discover_closure_records` against the real
  `docs/audit/closure-records.md` and asserts 21 drafts: 8 `CR- kind: work`, 1 `CR- kind:
  phase`, 2 `RS- kind: audit`, 10 `LG-`.** *Violation: any count other than 21, or any of the
  ten emitted under another prefix.* It must fail today with the `NotImplementedError` of
  §1(b) — the positive control the corpus already supplies.
- **A check that no emitted `LG-` carries a `slice:` whose value resolves to no roadmap row.**
  *Violation: a `slice:` naming nothing.* This is the clause that would have caught the
  derivation's original concern had it been real, and it must red on a deliberately broken
  fixture carrying `slice: SL-99999`.
- **A check that every emitted `LG-` carries a `work:` that does resolve**, once W37-6 has
  created the `WK-` rows. *Violation: a ledger with neither axis.* This is the substantive
  content of §1(e) — the ten are permitted to omit `slice:` because `work:` is present, not
  because both may be absent.
- **`status:` is read per record.** A fixture in which one of the ten states a slice that did
  not complete must produce `retired`, not `closed`. *Violation: ten records taking one status
  from one reading.*

---

## Where the wrong `plan-reviews.md` figures came from — a merged commit body, which cannot be corrected in place

**Not a ruling, filed here because it explains why a wrong figure survived three careful
readers and because the artifact carrying it cannot be edited.**

The lead routed Ruling 82's question with *"15 `###` headings, 12 records, three
undated … read as sub-content nested inside 'Plan review 9''s own section"*, corrected it on
its own initiative after the maintainer challenged it, and named an executor's report as the
source. The report was not the origin. `#585`'s **squash commit body on `main`** (`20b3025`)
reads:

> Fifteen `###` headings produce twelve records, and three of the fifteen carry no date at
> all, reading as sub-content nested inside another review's section rather than as
> independent records. No regex reaches that: the per-heading model may simply be the wrong
> shape for that file. Filed, not fixed.

Measured at `ffac8ba`: **14 headings, 10 records, four unaccounted** — the fourth being a filed
plan review, which the sentence above cannot describe because it counts only undated ones. The
figures reached the lead's brief through a chain in which nobody was careless: each reader was
citing a merged commit on `main`.

**Two things follow, and only the second is actionable.** First, `main`'s history is immutable
under the `main-protection` ruleset — squash bodies cannot be rewritten — so the wrong sentence
stays where it is and a reader who finds it has no in-place correction to find. Second, the
correction therefore has to live in a document that the commit's subject can be traced to.
[Ruling 82](2026-09-02-w37-commit-boundary-and-plan-reviews-shape-rulings.md) carries the measured figures and their probes; this paragraph names where
the superseded ones came from, so a reader arriving from `git log` has somewhere to land.

The general point, which is why it is filed rather than mentioned: **a figure in a commit
message is a citation target with no correction mechanism.** A count that a later reader will
act on belongs in a document that can be amended, and the commit body should point at it.

## Not ruled — and where each goes

| Item | Why not mine | Where it goes |
|---|---|---|
| **What `Ruling A1`, `A2` and `A3` are** (`2026-08-30-nt-0012-0013-0014-adoption.md:67,81,96`) | Surfaced by Ruling 83's measurement, but deciding whether a letter-suffixed id is a ruling, sub-content, or a legacy form to renumber is a family and id-form question under NT-0019 §1.2 and §1.7 — the same species the planner derived for the twelve. I have not enumerated the option set | **The planner**, as a derivation, then back here. It is a Ruling 83 precondition: the census cannot be cleared while three units are unclassified |
| **The three h1 ruling files** (`Ruling 59`, `60`, `61`) | A fact, not a decision — one ruling per file, so the multi-ruling splitter should not be reading them at all. Whether it currently tries is a code question | **W37-6's executor**, as a measurement during the census. If the splitter does try to split them, it is a new finding |
| **Whether `_discover_register`'s row unit needs the same treatment** | Ruling 83's property is worded to cover it, but the register's shape was not measured here and I will not assert a blind spot I have not seen | **W37-6's executor**, inside the census |
| **The commit boundary for Ruling 83's fix** | Ruling 81 settles the principle for this class; §2 applies it and names the one respect in which this fix differs. Merge order itself is the lead's | **The lead** |
| **Whether the ten W5 slices each completed** | Evidence, not a decision. §2 fixes the rule; reading ten records against it is execution | **W37-6's executor**, per Ruling 84 §4's fourth item |

## Provenance

Routed by the lead on 2026-09-02, both as maintainer requests. Ruling 83's property is the
maintainer's own words and its design is ruled here; Ruling 84 adopts a planner recommendation
one step smaller than as written, on two grounds the derivation did not have.

The lead's routing message corrected its own earlier `plan-reviews.md` figures unprompted, and
the corrected figures agree with the independent measurement filed as Rulings 81-82. Chasing where
the superseded ones came from produced the finding two sections above: they are quoted from a
merged commit body on `main`, which is why three readers passed them along unchanged. **No
figure in this record is taken from a relay** — every one was produced by executing the script
or reading the shipped source at `ffac8ba`, including the ones that turned out to agree with
what was relayed.
