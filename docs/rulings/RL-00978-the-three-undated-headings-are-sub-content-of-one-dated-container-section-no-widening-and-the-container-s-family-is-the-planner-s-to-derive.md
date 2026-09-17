---
id: RL-978
family: ruling
title: the three undated headings are sub-content of one dated container section; no widening, and the container's family is the planner's to derive
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-02
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-02-w37-commit-boundary-and-plan-reviews-shape-rulings.md
---

## RL-978 — the three undated headings are sub-content of one dated container section; no widening, and the container's family is the planner's to derive

### 1. Verified first, at `ffac8ba`

**(a) The heading census, and what the discovery function actually returns.**

```
$ grep -c '^### ' docs/closures/INDEX.md#plan-reviewsmd
14
```

and, importing `scripts/doc-id.py` and calling `_discover_plan_reviews(Path('.'))`:

```
RECORDS: 10
  2026-08-15  bodylines=  139  Plan review 2 — at WK-667's close and before Phase 1a's exit demo
  2026-08-22  bodylines=  102  Plan review 3 — at WK-661's close
  2026-08-24  bodylines=  123  Plan review 4 — at WK-692's close
  2026-08-27  bodylines=  158  Plan review 5 — at WK-664's close
  2026-08-27  bodylines=   32  Plan review 6 — at WK-665's close, before the Phase 1b exit demo
  2026-08-27  bodylines=  206  Plan review 7 — at WK-669's close
  2026-08-28  bodylines=  292  Plan review 8 — at WK-670's close
  2026-08-15  bodylines= 1094  Plan review 1 — at WK-663's close
  2026-08-30  bodylines=  328  Plan review 10 — at WK-671's second close
  2026-08-31  bodylines=  332  Plan review 11 — completing the review sequence at WK-671's close
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
| 1233 | `### Plan review 9 — at WK-671's close, 2026-08-30 — **FILED, with its drafting history intact**` | dated, but trailing text defeats the `\s*$` anchor |

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
drafts to `_check_legacy_file_not_silently_unrecognised` (`scripts/doc-id.py:1649-1677`). Its
docstring states the intent — *"zero discovered records from it is unrecognised shape, full
stop"* — and the message it raises states the consequence: *"this script's legacy pattern does
not match this file's real shape … migrate refuses to guess and silently report success
instead."* Its test is `if drafts: return` (`:1670`). With ten drafts it returns at that line
and neither string is ever printed. **The guard is all-or-nothing:
it catches a pattern that matches nothing and is blind to one that matches most of a file** —
which is the state every one of these discovery defects has been in, including the roadmap
no-op and the closure-record split.

**(c) The three undated headings are sub-content, and the file says so in its own words.**
They are the only `###` headings under the file's **only** `##` heading, at line 1155:

```
## Pending proposals — for the §14 review at WK-671's close (drafted 2026-08-29)
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
citations from a governed record, and RFC-937 §4 step 6 rewrites every citation across the
tracked tree. Whatever the disposition, those two citations need a target that resolves.

**(e) The planner already identified this section, and stopped one step short of a
destination.** W37-6's leaf plan §7.5, in the list of split rules that do not partition the
tree as written:

> **A dropped section is caught**; a misattributed one is not. `plan-reviews.md`'s
> `## Pending proposals` block (three `###` candidates, no §5.2 destination) would be either
> dropped — caught by acceptance (g)'s class 4, *"the concatenation of the outputs reproduces
> the input's body lines in order"* — or silently swallowed into the preceding `CR-`. Give it
> an explicit destination rather than letting the splitter choose.

**That is right, it predates this record, and it settles the disposition's direction without
naming the destination.** Two things it did not have and this record adds: the swallowing is
not hypothetical — it is happening now, measured in (b) — and the section is not the only
casualty, because Plan review 9 goes with it. The instruction *"give it an explicit
destination"* is the reason the family question is handed to the planner in §2 rather than
left to the migration, not a reason to consider it already answered.

**(f) A structural fact that no current check sees.** Because line 1155 is the file's only
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
of the closure-record defect exactly as the brief framed it, and it is also the error RL-974
corrected in the other direction: a governed document per heading, for things that are not
documents.

**Rejected: widen the pattern to `^##+` so the container itself becomes a `CR-`.** This mints
a closure record for a section whose own first sentence says it is not a review and binds
nothing. It is independently barred by RFC-937 §1.2: `CR`'s status subset is the single value
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

**Handed back, not ruled: which family and `kind:` the container takes.** RL-975's shape,
one day old and in this same Work: the decision-maker fixes the exclusion, the planner derives
the positive assignment against §5.2's full option set, and the derivation comes back to be
ruled. I have not enumerated that option set for this section, and assigning a family without
it is the *"predicate exercised once and trusted"* that
[`../plans/PL-00962-w37-6-the-twelve-non-close-records-in-closure-records-md-a-family-derivation.md`](../plans/PL-00962-w37-6-the-twelve-non-close-records-in-closure-records-md-a-family-derivation.md)
was written to prevent. Doing it here would be the same defect with a different author.

### 3. What it obliges

1. **`_REVIEW_HEADING_RE`'s `$` anchor is fixed so `Plan review 9` matches**, in the same
   shape `#585` used for `_CLOSURE_HEADING_RE` — a trailing-text capture group, not a looser
   date match. This is a code defect against merged W37-5, already tracked as the lead's task
   *"four discovery functions written against the fixture shape"*; (b) above is its measured
   blast radius and is the evidence that it destroys a record rather than merely missing one.
2. **The pattern is not widened to match an undated heading, at any heading level.** Whatever
   handles the container section handles it as a section, not as a fifteenth pattern match.
3. **The planner derives the container's family and `kind:`**, under RFC-937 §5.2 and §1.2,
   with four constraints established here and not re-derivable from the heading alone:
   - `CR-` is excluded, on §1.2's status subset and `kind:` vocabulary and on the section's own
     first sentence.
   - **The unit boundary is the `##` section — lines 1155–1232 — not the three `###` inside
     it**, and not a fold into `Plan review 1`.
   - RL-989 acceptance (g) class 4 — *"the concatenation of the outputs reproduces the
     input's body lines in order"* — leaves exactly two placements: the section becomes its own
     record, or it becomes `Plan review 9`'s preamble by that record's boundary starting at
     1155 instead of 1233. Both must be tested; a third is not available without reordering the
     file.
   - **Whichever is chosen, Plan review 9's two citations of *"the unnumbered 'Pending
     proposals' section above"* must resolve after the rewrite.** The preamble option makes
     that self-referential and the derivation must say what it rewrites to; that is a real
     cost of the option, not a disqualification of it.
4. **The mis-nesting in §1(f) is recorded, not fixed here.** Reviews 9–11 sitting under a `##`
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
| *"`docs/closures/INDEX.md#plan-reviewsmd` has 15 `###` headings"* | **14** (`grep -c '^### '`) | — |
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
| **The container section's family and `kind:`** | RL-975's precedent: the exclusion is the decision-maker's, the positive assignment is derived by the planner against §5.2's full option set and ruled afterwards. I have not done that enumeration | **The planner**, with RL-978 §3 item 3's four constraints. Comes back here to be ruled |
| **The `$`-anchor fix in `_REVIEW_HEADING_RE`** | A code defect in merged W37-5, not a spec-versus-code conflict — the same species as the closure-record split already fixed in `#585` | **The lead**, folded into the existing task for the four discovery functions. §1(b) supplies the blast radius it did not have |
| **`plan-reviews.md`'s heading mis-nesting (§1(f))** | A structural defect in a governed document, not a decision about what the standard means | **The lead**, as a finding. Fixing it before the migration is cheaper than after, but it blocks nothing |
| **Whether the executor's branch merges before or after any other open PR** | Merge order is the lead's, and `CLAUDE.md`'s standing rule reserves every merge to it. RL-977 fixes that the branch merges *on its own*, not when | **The lead** |

## Provenance

Routed by the lead on 2026-09-02 under the 2026-09-01 delegation, alongside an explicit
invitation to decline either question. Neither was declined; the second was ruled narrower
than it was asked, and the narrowing is stated in RL-978 §2 rather than left as silence.
Both rulings were written against `ffac8ba` with every script claim produced by executing the
script.
