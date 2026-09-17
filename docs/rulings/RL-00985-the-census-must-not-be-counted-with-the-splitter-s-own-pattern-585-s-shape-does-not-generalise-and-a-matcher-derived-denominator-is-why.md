---
id: RL-985
family: ruling
title: the census must not be counted with the splitter's own pattern; `#585`'s shape does not generalise, and a matcher-derived denominator is why
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-02
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-02-w37-guard-arithmetic-and-ledger-family-rulings.md
---

# The split guard's arithmetic, and the family the ten WK-661 slice records take, ruled (2026-09-02)

**What this is.** Two questions the maintainer asked for as rulings, routed by the lead on
2026-09-02. The first is a design question stated as a property with the design left open; the
second is a family assignment [RL-975](RL-00975-a-pre-run-predicate-is-insufficient-as-the-plan-states-it-and-it-is-also-mis-sized-by-a-factor-of-four-the-remedy-is-an-enumerated-table-whose-positive-control-the-corpus-already-supplies.md)
reserved and the planner's derivation handed back. They are ruled below as Rulings 83 and 84.

**RL-985's short answer is that `#585`'s approach does not generalise, and the reason is
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

**RL-986's short answer is that the obstacle is already gone.** The planner's derivation
rejected `LG-` on one measured ground — that `slice:` is required and unsatisfiable — and that
ground was refuted in
[`RL-00999-the-phase-section-is-plain-fields-under-its-heading-the-fence-requirement-in-scan-phase-sections-is-the-defect-and-its-unbounded-lookahead-is-what-makes-the-failure-silent-instead-of-loud.md`](RL-00999-the-phase-section-is-plain-fields-under-its-heading-the-fence-requirement-in-scan-phase-sections-is-the-defect-and-its-unbounded-lookahead-is-what-makes-the-failure-silent-instead-of-loud.md)'s
closing section without a ruling number being minted, because a refuted premise decides
nothing on its own. What it left undecided is the adoption, which RL-975 and the derivation
both reserved here. That is what RL-986 does, in a form one step smaller than the
derivation's own recommendation.

**Rulings 81 and 82 are the sibling record filed earlier the same day**, merged as `0e9f620`
(PR #589) while this branch was open. 83 and 84 continue the sequence with no gap.

## Authority

- **Both were routed by the lead under the maintainer's delegation of 2026-09-01**, recorded at
  [`RL-00940-the-maintainer-s-delegation-and-rfc-937-s-precedence-recorded-2026-09-01.md`](RL-00940-the-maintainer-s-delegation-and-rfc-937-s-precedence-recorded-2026-09-01.md)
  §1, and neither falls in its §2 exclusions: neither is a fact only the maintainer holds,
  neither accepts a Work, Phase or Project close, and neither amends `CLAUDE.md`.
- **RL-985 was asked for as a ruling in the maintainer's own words**, relayed by the lead:
  *"'Found nothing means already migrated' was a fixture-corpus assumption; the real tree needs
  the arithmetic to close. How — options, trade-offs, a recommendation — is a ruling to bring
  me, not something to pick silently."* The property is the maintainer's; the design is what is
  ruled here.
- **RL-986 is the decision RL-975 and the derivation both reserved.**
  [`../plans/PL-00962-w37-6-the-twelve-non-close-records-in-closure-records-md-a-family-derivation.md`](../plans/PL-00962-w37-6-the-twelve-non-close-records-in-closure-records-md-a-family-derivation.md)
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
  §1(g)'s roadmap counts re-measure unchanged at `59bba94` — 56 leading rows over 41 distinct
  ids — so every citation below holds at both trees. **The measurement tree stays `ffac8ba`** — that is a
  fixed fact; which commit is `main`'s tip is not, and is why it is not restated as one below.
- **Re-read under [`delivery-process.md`](../process/delivery-process.md) §15 Rule 10** —
  *"a branch open when a ruling merges is re-read against that ruling before the branch itself
  merges."* Rulings 81 and 82 merged during this branch's life and the re-read was done: Ruling
  81's commit-boundary reasoning is applied by RL-985 §2 and its citation updated from an
  open PR to the merged record; RL-978's plan-reviews measurement is cited in §1(d); neither
  changes a conclusion here. PR #590 corrects the roadmap row's plan-reviews figures to the same
  values and attributes them to *"a report"* — the section below names what that report was
  quoting, which is the one thing it does not carry.
- **Neither ruling edits [`RFC-937`](../rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md) §1,
  [`document-ids.md`](../process/document-ids.md), or any template.** RL-986 in particular
  needs no template edit, which is the respect in which it is smaller than the recommendation
  it adopts.
- **No filed plan is amended.** W37-6's leaf plan is frozen at its date; the two obligations
  these rulings put on that slice are stated here and are a new dated artifact, not an edit.

## Acceptance Standard

**Why a ruling record carries this heading.** `audit-docs.py` check 28 classifies every dated
file in `docs/plans/` outside four suffixes as a plan needing this section, while
`check_plan_acceptance_standard`'s own docstring disclaims exactly that scope. That
disagreement is register finding F68 — see [`../findings/register.md`](../findings/register.md) —
carried forward with RFC-937's migration as its trigger. It is honoured here, and the check is
not patched from this branch.

1. `git grep -n '^#\+ Ruling ' docs/plans/` shows 83–84 filling the gap immediately after
   82 with no duplicate and no skip, counting 81 and 82, merged as `0e9f620`.
2. Each `### 2. Ruled` subsection names the chosen option **and every rejected option**, with
   the measured evidence that separated them. RL-985 additionally carries the maintainer's
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

## RL-985 — the census must not be counted with the splitter's own pattern; `#585`'s shape does not generalise, and a matcher-derived denominator is why

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
NotImplementedError: migrate: …/docs/closures/INDEX.md#closure-recordsmd, heading
'WK-661 — the GLM spine' (2026-08-15) is not yet closed -- migrate cannot assign a
family a governed document does not have (task #31).
```

`migrate` calls it at `:1828` inside no `try`, so control never reaches the guard at
`:1829-1831`. That guard is unreachable for closure-records on today's tree, and its blind spot
there is hidden rather than absent — it will surface the moment RL-986 replaces the raise.

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
docs/rulings/RL-00949-rfc-897-slice-2-s-census-csv-and-fr-72-the-test-is-overbroad-the.md:1:# RL-949 — …
docs/rulings/RL-00950-rl-949-3-point-2-s-fetch-path-is-broken-against-github-com-resolved-by.md:1:# RL-950 — …
docs/rulings/RL-00951-rl-947-s-tombstone-gains-per-file-stubs-watched-by-a-new-check-not-left.md:1:# RL-951 — …
```

The three `###` fail on **both** level and id form — their ids are letter-suffixed, and
`(\d+)` cannot match them:

```
docs/rulings/RL-00902-rfc-842-s-credential-lifetime-rule-lands-in-claude-skills-secret-hygiene.md:16:### RL-902 — …
docs/rulings/RL-00903-rfc-842-s-search-by-shape-rule-lands-in-claude-skills-close-workstream.md:16:### RL-903 — …
docs/rulings/RL-00904-rfc-843-s-remove-the-relay-lands-in-delivery-process-md-15.md:16:### RL-904 — …
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
| `_discover_plan_reviews` | 1265 | `_REVIEW_HEADING_RE` | **4 headings**, one of them a filed review (RL-978) |
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

**(g) The work population — and this ruling's own thesis, demonstrated on this ruling's own
evidence.** Measured at `59bba94`:

```
$ grep -cE '^\|\s*\*\*W[0-9]+[a-z]?\*\*'          docs/roadmap.md   → 30   open works
$ grep -cE '^\|\s*~~\*\*W[0-9]+[a-z]?\*\*~~'      docs/roadmap.md   → 26   closed works
$ grep -cE '^\|\s*(~~)?\*\*W[0-9]+[a-z]?\*\*'     docs/roadmap.md   → 56   leading rows
  distinct ids across those 56 rows                                 → 41
```

Many rows are written `| ~~**WK-657**~~ ✔ | …`. **A pattern anchored on `\*\*W` cannot match a
struck id**, so 26 of the 56 rows are invisible to it.

**An earlier draft of this section called `30` a count of leading rows and offered `41 versus
30` as two correct readings of one measurement. That was wrong, and the way it was wrong is
this ruling's subject.** A denominator derived from a matcher, blind to a form variation the
corpus actually carries — strikethrough here, a letter-suffixed id in §1(c)'s `RL-902` — is
the same defect one level up, sitting inside the evidence for the rule against it. It is
recorded rather than quietly fixed, because a ruling that could not survive its own predicate
would not deserve to bind anything.

**Two readers reached `30` independently before anyone opened the file, and that felt like
corroboration.** It was one blind spot reached twice: both counts were taken with a pattern
carrying the same assumption, so they could not have disagreed. Agreement between two
measurements is evidence only when they could have failed differently.

**And the natural repair — reading the 30 as "the open works" — does not survive either.**
Decoration is typography here, not status. In the *"Phase 1b status"* table, `| **WK-661** |`
carries no strikethrough while its own Status cell reads `✔ **closed 2026-08-22**`, and
`| ~~**WK-665**~~ ✔ |` is struck **three rows below it in the same table**. `WK-661` appears in three
leading rows altogether — undecorated once, struck twice. **Status lives in the Status cell;
the id's decoration tracks nothing reliably**, so neither `30` nor `26` is a count of anything
about a work's state.

**What is actually true, and the two open questions it exposes.** The population is **41
distinct work ids across 56 leading rows**, because a work may head a row in more than one
table. §4 step 3 says *"each Work a `WK-` row"*, so:

1. **Do all 41 convert, or only some?** Whether the works recorded as closed become `WK-` rows
   with `status: closed` under their milestone, or do not convert at all, is undecided.
2. **Which of a work's rows becomes *the* row?** With 56 rows for 41 works, one work's several
   rows must be merged or one chosen. Nothing in §4 step 3 says which, and this question was
   not visible at all while the count was believed to be one row per work.

Both are design questions about what the migrated roadmap holds — exactly what a census
surfaces and a matcher-derived count cannot. Neither is *"two readings of one measurement"*.

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
| (a) | **Expected-count constant per call site** — `assert len(drafts) == 11` | **Rejected.** A transcribed count, stale on the next filed review, and it cannot name which unit was lost. It is the defect class RL-981 struck `_ROW_FIELDS` for, re-created in the guard that exists to catch it |
| (b) | **`#585`'s shape, generalised** — widen each matcher, classify every match, raise on the unclassifiable | **Rejected as sufficient, adopted as necessary.** It is the right treatment for a *known* variation and it is why closure-records is now correct. It cannot close the arithmetic, because its denominator is the widened matcher: (c)'s letter-id headings are invisible to any count taken this way, and widening again only moves the boundary |
| (c) | **Maintained exclusion list per file** — an explicit table of headings that are deliberately not records | **Rejected as the primary mechanism, kept as bucket 3.** It closes the arithmetic, but the list is itself a transcribed policy with the same staleness failure as (a). Acceptable only for what cannot be derived, and only with a reason per entry |
| (d) | **Structural invariant, no list** — no output record's body may contain a heading at the split's own level | **Adopted, as the derivation behind bucket 2.** Needs nothing maintained and would have caught Plan review 9 immediately, since Plan review 1's body contains four `###` headings. Alone it is not enough: it says a record swallowed something, not that a source unit went unaccounted for |
| (e) | **(d) plus a level-independent census, buckets 1–3 balancing** | **Recommended and ruled.** The census is the only term that cannot be gamed by widening a regex, and the only one that surfaces a unit whose *id form* — not its position — is unexpected. It is not a new idea here: §1(f)'s roadmap guard already reads a post-migration marker instead of asking the legacy matcher, and this generalises that to an arithmetic instead of a yes/no |

**Why the denominator is the whole ruling.** Every previous fix in this class widened a
matcher. Each was correct and each left the same hole, because the thing measuring coverage
and the thing providing it were the same expression. RL-981 struck `_ROW_FIELDS` for
transcribing a policy the templates already declared; this is the same principle turned on the
guard: **a check may not derive its own denominator from the thing it is checking.**

**Rejected: leaving the guard as it is and relying on RL-989 acceptance (g) class 4.** Class
4 requires *"the concatenation of the outputs reproduces the input's body lines in order"*. Every
defect in this class **passes** it — the lines are all present, in order, in the wrong record.
W37-6's leaf plan §7.5 already says so in its own words: *"A dropped section is caught; a
misattributed one is not."* Class 4 cannot be the arithmetic.

**Rejected: deferring this to W37-6.** The guard fix is testable today against a corpus that
already produces four distinct violations, and W37-6's go-ahead is withheld. This follows
RL-977's reasoning and differs from it in one respect that is stated rather than
smoothed: this change **does** alter behaviour on the real tree — `migrate` will raise where it
now succeeds. That is not a red gate, because `migrate` is not run by CI and the tests exercise
`tests/fixtures/docs-migration`, not the real corpus. It is the intended effect.

### 3. What it obliges

1. **The census runs before W37-6, not during it.** Every unclassified unit is resolved and
   recorded ahead of the go-ahead. This is the maintainer's instruction on RL-986 —
   *"so a run is not halted on it on the day"* — applied to the same mechanism: a guard that
   halts loudly is only an improvement if what it halts on has already been cleared.
2. **The six ruling headings of §1(c) get a disposition each.** The three h1 files are one
   ruling per file and need no split; the three `RL-902`–`A3` carry an id form
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
  form the splitter's regex cannot express** — the `RL-902` shape, in a fixture. The census
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
- **A decorated id is counted.** A fixture row written `| ~~**WK-657**~~ ✔ |` must appear in the
  census exactly like `| **WK-657** |`. *Violation: a row whose id carries markup the counting
  pattern does not model.* This is §1(g)'s own failure turned into a test: it went undetected
  in this record's first draft and in the lead's independent count, and a form variation that
  fooled two readers is the one a fixture must carry.

---
