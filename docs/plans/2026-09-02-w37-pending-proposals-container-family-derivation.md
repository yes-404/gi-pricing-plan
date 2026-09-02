# The `Pending proposals` container: its family and `kind:` — a derivation for ruling (2026-09-02)

> **For agentic workers:** this is a derivation, not a plan and not a ruling. It enumerates an
> option set and recommends one. It binds nothing until the decision-maker rules on it.

**Goal:** answer Ruling 82 §3 item 3 — *"The planner derives the container's family and
`kind:`, under NT-0019 §5.2 and §1.2"* — so the unit at
`docs/audit/plan-reviews.md:1155-1232` has a destination and Ruling 83's census can close.

**Spec:** [`../notes/0019-one-id-per-document.md`](../notes/0019-one-id-per-document.md) §1.2,
§1.7, §4 step 2 and §5.2.

**Tree:** every line number, count and quotation below was read or produced at **`b648c22`**.
**Re-verified unchanged at `01bd0bd`** (`main` after `e7e1d24` and `01bd0bd` landed): the file
still carries 14 `###` headings and exactly one level-2 heading, the container still opens at
1155, and all fourteen line-number citations of §7 still resolve as counted. The re-read is
`delivery-process.md` §15 Rule 10's.

## Acceptance Standard

Complete when every item holds. Each is a violation that must be detectable.

1. **Ruling 82's four constraints are each honoured explicitly**, by name, and any one found
   to be incomplete is reported rather than quietly widened. *Violation: a constraint applied
   silently, or a fifth constraint invented without saying so.*
2. **Both surviving placements are tested against Ruling 68 acceptance (g) class 4**, and the
   test's result is stated even where it fails to discriminate. *Violation: naming class 4 as
   the discriminator without showing what it returns for each.*
3. **What each citation of the container rewrites to is stated per placement**, not in
   general. *Violation: a placement recommended without saying what the citing documents then
   say.*
4. **The option set is enumerated against §1.2's full family table**, not against a shortlist.
   *Violation: a family excluded without a reason drawn from §1.2's own columns.*
5. **The recommendation is handed over, not applied.** *Violation: this document changing any
   governed document, or reading as though the question were settled.*
6. **`python3 scripts/audit-docs.py` and `python3 scripts/req-coverage.py` both exit 0.**
   *Violation: any non-zero exit.*

## Global Constraints

- **The decision is the decision-maker's.** Ruling 82 fixed the exclusion; this derives the
  positive assignment and returns it. That is Ruling 78's shape, one day older.
- **No filed plan or frozen record is edited.** `docs/audit/plan-reviews.md` is not touched.
- **Requirement ids and section numbers are permanent** (`CLAUDE.md` §5).

---

## 1. What the unit is

Ruling 82 fixes the boundary as the whole `##` section, lines **1155-1232**. Confirmed: 1155
is the `##` heading, 1232 is the closing `---`, and 1233 opens `### Plan review 9`.

**It declares itself.** Its first sentence: *"**This is not a plan review and binds nothing.**
It has no review number, no five questions and no maintainer acceptance line, because the §14
trigger — a workstream close — has not fired."*

**It exists to be a durable home.** *"It exists because two rule proposals had no durable
home: one lived only in the comments of `#370`, now merged and closed, and the other was never
written down at all."* It cites `CLAUDE.md` §12's rule that a decision lands as a dated
artifact rather than in chat.

**It contains two rule proposals and one disposition** — `### Candidate A`, `### Candidate B`,
`### Also carried, and not a new rule` — plus a block-quoted correction recording an upstream
fix made while the entry was open.

**And it states a rule that another record applies by name.** *"A rule number is an
identifier, and an identifier assigned before the thing exists is the same defect as a count
written before the list is closed. **Numbering happens at acceptance.**"*

That last fact is the one that matters, and §2 shows why.

---

## 2. Ruling 82 says two citations. There are three, and the third is from another record

Ruling 82 §3 item 3's fourth constraint: *"Whichever is chosen, **Plan review 9's two
citations** of 'the unnumbered "Pending proposals" section above' must resolve after the
rewrite."* Both exist and are correctly described:

| Line | Record | Text |
|---|---|---|
| 1994 | Plan review 9 | *"Candidates A and B, from the unnumbered "Pending proposals" section above, formally taken up here"* |
| 2121 | Plan review 9 | *"Review 8 and the unnumbered "Pending proposals" section, both above in this document — read directly here rather than re-derived"* |

**A third citation exists, and it is not Plan review 9's.** At line **2645**, inside
**Plan review 11** (which opens at 2485):

> *"with numbering deliberately deferred to maintainer acceptance — correct, per the "Pending
> proposals" section's **own rule** that "numbering happens at acceptance.""*

This is a different species from the other two. Plan review 9's citations are *provenance* —
where the candidates came from. Plan review 11's cites the container **as a normative source**,
quoting a rule it states and applying it to judge another record's conduct.

**Reported rather than folded in silently**, per Ruling 82's own framing of what a derivation
owes: the constraint list said two, the corpus has three, and the third changes the cost of
one of the two permitted placements. It does not change the boundary, the `CR-` exclusion, or
the two-placement finding — those hold exactly as ruled.

**The container's self-description and its use disagree.** It says it *"binds nothing"*; a
later review cites its rule to settle a question. Both are true: it bound nothing when
written, and it is a source now. A family assignment has to serve the second reading, because
that is the one a future reader follows a citation into.

---

## 3. §5.2 has no row for it, which is the Ruling 77 situation

The standard's three statements about this file all describe reviews only:

| Where | What it says |
|---|---|
| §4 step 2 | *"`plan-reviews.md` → one `CR-` per review"* |
| §5.2 | *"split into `CR-` files (`work`, `review`); preambles → `closures/README.md`"* |
| D9 | *"`closure-records.md` and `plan-reviews.md` split into `CR-` files"* — one unit per file |

The container is **not a review** (§1) and **not a preamble** — a preamble precedes the first
record, and this sits at 1155, after Plan review 1 opens at 1061. So no §5.2 row reaches it.

That is precisely the position Ruling 77 resolved for the two orphan `docs/audit/` files: no
row, so the family is derived under §5.4's bespoke rule and ruled afterwards. This derivation
takes the same route.

---

## 4. The option set, against §1.2's full family table

Every document family in §1.2, with the column that admits or excludes it.

| Family | §1.2 unit / `kind:` | Verdict |
|---|---|---|
| `CR` Closure | *"one work, phase or review close"*; `work · phase · review`; status subset is the single value `active` | **Excluded by Ruling 82**, on those grounds and the section's own first sentence |
| `PL` Plan | *"one plan"*; `map · leaf · review · handover` | **Excluded.** It is not a plan, and no `kind:` term describes a set of rule proposals |
| `RL` Ruling | *"one ruling"* | **Excluded.** It rules nothing; it proposes, and says so |
| `RS` Research | *"one spike, measurement or audit"*; `spike · measurement · audit` | **Excluded.** It measures nothing and audits nothing |
| `LG` Ledger | *"one slice's execution"* | **Excluded.** No slice, no execution |
| `FD` Finding | *"one finding"*, register row + essay | **Excluded**, though it calls its own first observation *"the first finding"*. That observation was recorded and fixed upstream inside the section; there is no open finding to carry a register row |
| `WF` Workflow · `ADR` Decision | one journey / one decision | **Excluded.** Neither shape |
| **`RFC` Proposal** | ***"one topic"***; frozen; `draft → active → closed \| retired \| superseded`; `kind:` **`enhancement · process · incident`** | **Recommended.** Every column fits without strain |

**Why `RFC- kind: process` fits on each column rather than merely being left over:**

- **Family name.** The section is two *rule proposals*. `RFC` is the proposal family.
- **Unit — "one topic".** Both candidates are rules for the same rule set (`delivery-process.md`
  §15), and the third heading disposes of a proposal against that same set. One topic, three
  parts.
- **`kind: process`.** The topic is process rules, which is the term's own subject.
- **Mutability — frozen.** It is a dated draft, superseded by being taken up.
- **Status — `closed`.** §1.2a defines `closed` as *"completed its purpose — answered,
  delivered, sealed, landed, resolved, **promoted**"*, and names "promoted" as one of the words
  it replaces. Plan review 9 §5.4 promoted both candidates. `superseded` is the wrong word
  because §1.2a reserves it for *"replaced by a named successor in `superseded_by:`"* and the
  successor here is a proposal inside another record, not a document that replaces this one.

---

## 5. The two placements, tested against class 4 — and what actually discriminates

Ruling 68 acceptance (g) class 4 permits *"a split, where the concatenation of the outputs
reproduces the input's body lines in order"*.

| Placement | Split points | Class 4 |
|---|---|---|
| **P1 — its own record** | Plan review 1 = 1061-1154; container = 1155-1232; Plan review 9 = 1233-2155 | **Passes.** Contiguous, in order, nothing dropped |
| **P2 — Plan review 9's preamble** | Plan review 1 = 1061-1154; Plan review 9 = 1155-2155 | **Passes.** Also contiguous and in order |

**Class 4 does not discriminate**, exactly as Ruling 82 said when it left two placements
standing. The discriminator is what the three citations of §2 say afterwards.

| Citation | Under **P1** | Under **P2** |
|---|---|---|
| 1994 (Plan review 9) | *"from `RFC-<n>`"* — a cross-record reference, resolvable | becomes self-referential: the record cites its own preamble. Ruling 82 named this cost |
| 2121 (Plan review 9) | *"`CR-<review 8>` and `RFC-<n>`"* — both resolve. *"both above in this document"* must go either way, since after the split there is no "this document" | same self-reference, plus the same lost phrase |
| **2645 (Plan review 11)** | *"per `RFC-<n>`'s rule that 'numbering happens at acceptance'"* — **resolves, and keeps the attribution**| **the rule is attributed to Plan review 9**, a record that did not state it and whose own text records taking the candidates *up*, not writing the rule |

**P2 misattributes a normative rule across records.** That is the deciding difference, and it
is visible only once the third citation is counted. §1.7's resolver is
`\b(FR\|NFR\|DEP\|OQ\|WK\|SL\|WF\|ADR\|RFC\|PL\|LG\|RL\|RS\|CR\|FD)-0*(\d+)\b`; under P1 the
container has an id the resolver reaches, and under P2 it has none.

**Recommended: P1 with `RFC-`, `kind: process`, `status: closed`, `created: 2026-08-29`
(the date in its own heading), `owner: planner`, `was:` `docs/audit/plan-reviews.md`.**

---

## 6. What it would oblige

1. **`_discover_plan_reviews` gains a non-review record**, so the file's split is *"one `CR-`
   per review **and** one `RFC-` for the container"*. Ruling 82 item 2 forbids widening
   `_REVIEW_HEADING_RE` to reach it; the container is found as a section, not as a fifteenth
   pattern match — which is what Ruling 82 meant by *"whatever handles the container section
   handles it as a section"*.

   **And the obvious implementation of that sentence is wrong.** `grep -c '^##[^#]'` over the
   whole 2816-line file returns **1**: line 1155 is the only level-2 heading in the document.
   A rule reading *"from the `##` to the next `##`"* therefore yields **1155 to end of file** —
   the container plus Plan reviews 9, 10 and 11. The section must be closed at the next
   **record** heading (`### Plan review 9`, line 1233), not at the next heading of its own
   level. This is the same mis-nesting Ruling 82 §3 item 4 recorded as the lead's finding,
   showing up as an implementation trap rather than as a rendering defect, and it is why the
   boundary Ruling 82 fixed by line number cannot be re-derived from heading level alone.
2. **§5.2's row gains this destination**, or the migration carries it as a bespoke derivation
   the way Ruling 77's two files are carried. Either is consistent; the second needs no
   standard edit.
3. **Three citations rewrite**, not two, and 2645's is the one that must keep its attribution.
4. **The phrase *"both above in this document"* at 2121 stops being true** under either
   placement and needs replacing, not just re-pointing. Ruling 82's constraint says the
   citations must *resolve*; this one resolves and reads false.
5. **`REDIRECTS.csv` carries a row keyed on the section**, since one source file yields
   twelve records and a path-level row cannot distinguish them.
6. **The three `###` candidates stay body inside the `RFC-`.** This satisfies the standing
   acceptance item in
   [`2026-09-02-w37-6-twelve-non-close-records-derivation.md`](2026-09-02-w37-6-twelve-non-close-records-derivation.md)
   — *"Violation: a `CR- kind: review` minted from any of the three `## Pending proposals`
   candidates, or any of the three dropped"* — in both directions at once: none is minted as a
   record, and none is dropped, because the section that contains them becomes one.

---

## 7. One thing this measurement surfaced that is not this question

**Fourteen line-number citations point into the two files being split**, and a path-level
rewrite silently corrupts every one of them:

| Cited file | Line-number citations | Citing files include |
|---|---|---|
| `docs/audit/plan-reviews.md` | 11 | `.claude/skills/close-workstream/SKILL.md:646`, `docs/audit/register.md` (×4), two filed plans, and the file itself (×2) |
| `docs/audit/register.md` | 3 | — |

A citation of the form `docs/audit/plan-reviews.md:1994-2006` **is** caught by the legacy-form
sweep — its `docs/audit/` prefix matches — so it is detected. But detection is not repair: the
correct rewrite needs the line number **re-derived inside the destination record**, because
line 1994 of a 2816-line file is not line 1994 of the ~920-line record it lands in. A rewrite
that changes only the path produces a citation that resolves to a file and points at the wrong
place in it, which is worse than one that fails loudly.

One of the fourteen is inside an instrument (`close-workstream`), which puts it in Ruling 66's
territory as well.

**Not decided here.** It belongs with the census and with the citation-rewrite step, and it is
recorded because this derivation is what found it.

---

## 8. What this derivation does not do

- It does not rule. Ruling 82 fixed the exclusion; this returns the positive assignment.
- It does not edit `docs/audit/plan-reviews.md`, the standard, or any filed plan.
- It does not fix the heading mis-nesting Ruling 82 §3 item 4 recorded as the lead's, and it
  does not depend on that being fixed first.
- It does not decide §7, which has a different owner.
