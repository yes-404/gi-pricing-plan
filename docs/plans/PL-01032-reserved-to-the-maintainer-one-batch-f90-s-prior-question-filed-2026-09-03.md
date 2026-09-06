---
id: PL-1032
family: plan
kind: leaf
title: Reserved to the maintainer — one batch: F90's prior question (filed 2026-09-03)
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-09-03
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-09-03-w37-6-maintainer-decisions.md
---

# Reserved to the maintainer — one batch: F90's prior question (filed 2026-09-03)

**Assembled by the planner at `796cd07`, 2026-09-03 00:00 UTC.** The instructions it answers are the maintainer's of 2026-09-02; the file carries the date it was filed, which crossed midnight while it was written. Everything reserved to the maintainer and not
already ruled, collected into one document per the maintainer's standing rule 4 of
[`…-second-withholding-and-standing-rules.md`](../rulings/RL-00976-w37-6-withheld-a-second-time-and-five-standing-rules-on-method-the-maintainer-s-2026-09-02.md)
§4: *"Do not route me one call at a time. The planner collects everything reserved to me,
prices the options, and brings one dated ruling document per day; I fill it in one pass and it
lands as the artifact. Chat is for questions, not decisions."*

**This document decides nothing.** Every Decision line below is blank and is the maintainer's.
`CLAUDE.md` §12: every decision lands as a dated artifact, never in chat.

**Next free ruling number is 96** — `git grep -h -oE '^#+ Ruling [0-9]+' -- docs/plans/` at
`796cd07` gives a maximum of 95, no gaps. No `Ruling <n>` heading is written here, so the
census is unmoved until a decision is filled in.

## Authority

- **One item, D1, with one consequence, D2.** Both turn on `CLAUDE.md` §12's reservation of
  *"an amendment to what this file requires"* and on the maintainer's own dated instruction of
  2026-09-02, which D2 asks whether to re-issue.
- **Not re-raised**: `CLAUDE.md` §2's three-versus-four-workflows question, ruled and merged by
  the maintainer's own amendment in `796cd07` (#655), which edits `CLAUDE.md` line 50.
- **Not in this batch, because each is already dispositioned**: F87 (a disclosure), F92 (a
  declared deferral stamped in W37-11), `DESTINATION_ONLY` (a register row), the eighth class
  (adopted), §5.4's three-part gap condition (accepted) — all four at
  [`…-second-withholding-and-standing-rules.md`](../rulings/RL-00976-w37-6-withheld-a-second-time-and-five-standing-rules-on-method-the-maintainer-s-2026-09-02.md)
  §3 and §2.3. F89, F88 limb 2 and F94 are the lead's or carry their own decay event.

## Acceptance Standard

The violation this record must make detectable: **a maintainer decision taken against a
narrower question than the one that governs, or against a remedy priced from a claim that was
never run.** Each item is stated as the violation.

1. **The prior question is put as the prior question, not as a fifth option.** *Violation:* D1
   presented as a menu extension of F90's four, which is the framing that produced the defect.
2. **Every claim about what a remedy achieves is measured, not predicted.** *Violation:* a
   figure here without the tree it was measured at and the predicate it was measured with, or
   an option scored by reading the code rather than running it (`CLAUDE.md` §13).
3. **The order that is contradicted is quoted, not paraphrased.** *Violation:* D2 describing
   the maintainer's 2026-09-02 instruction in the planner's words.
4. **No Decision line is filled in any hand but the maintainer's.** *Violation:* a date or a
   verdict below written by the planner, the lead or an executor.
5. **This record is not the state.** *Violation:* a later document citing this file for W37-6
   status rather than `register-owed.py W37-6` or the roadmap row.

---

## D1 — Does `check_shape` apply at all to a body the migration carried over verbatim from a pre-standard file?

### The question

`check_shape` (`audit-docs.py` check 37) derives a required set of body sections from a family's
template and requires every migrated document of that family to carry them. **W37-6's migration
does not author documents from templates. It stamps a header onto bodies that already exist**,
written before the standard did. F90's four listed options all ask *how do we make the check
pass on these bodies*. The prior question is **whether the check has jurisdiction over them at
all**, and it governs every one of them.

### Why the four options cannot answer it — measured, not argued

From the F90 amendment on PR #656 (unmerged), executor-measured at `origin/main` `32fc63c`
against a disposable snapshot, using F90's own reproducer verbatim:

| Required section, from `docs/_templates/RL.md` | Exact at `##` | Any depth | Any depth, ordinal stripped |
|---|---|---|---|
| `Question` | 0 | 0 | 0 |
| `Ruling` | 0 | 0 | 0 |
| `Rationale` | 0 | 0 | 0 |
| `Acceptance — the violation that must become detectable` | 0 | 0 | **30** |

**Three of the four required sections do not exist in the corpus under any name, at any depth,
numbered or not.** No detector change can make one migrated ruling pass, so options 1, 2 and 4
are scoped against a mismatch that is not the binding one. Option 3 (backfill) leaves the same
three sections missing on the other 189.

**Option 4 specifically does not do what F90 says it does.** F90 calls it *"the only option of
the four that makes RL-984 pass as measured."* Run end to end, check-37 ruling failures go
**95 → 95**.

### The size of what a decision has to cover

**284 of 529 documents, across six families, not 95 across one** — measured by running
`migrate()` to completion on a disposable snapshot of `32fc63c`, then the real `check_shape()`
with `_ID_SCOPE_ROOTS` widened, bucketing failures by the family named in each message:

| plan | ruling | closure | proposal | ledger | research | total |
|---|---|---|---|---|---|---|
| 119 | 95 | 38 | 20 | 10 | 2 | **284** |

Every red is the same cause. A remedy scoped to `family: ruling` leaves 189 documents red on it.

**Two corrections to what was relayed to the planner while this was assembled, each recorded
because acting on the relayed form would misprice the decision:**

- **A re-measurement at `796cd07` is reported as 285 red across the same six families** (plan
  120, the other five unchanged), the +1 being the one `docs/plans/` document `796cd07` adds
  over `32fc63c`. **Relayed to the planner, not verified by it**, and its denominator is *not*
  the 529 above: 291 is the count of document drafts the run *creates*, while 529 is the count
  check 37 *examines*. **The two figures agree; the denominators do not, and they must not be
  collapsed.**
- **Heading-text normalisation is not an unnamed second barrier.** It was put to the planner
  that no listed option addresses `### 4. Acceptance — …` against the literal required
  `Acceptance — …`. **F90's own amendment names it**: §B states *"a depth-agnostic literal match
  still finds nothing. A detector has to be depth-agnostic **and** tolerant of an ordinal prefix"*,
  its table's third column is that predicate, and §D's fifth entry is the remedy shape it
  implies. The finding is on record; what is missing is a disposition, which is D1.

### The options for the prior question

| | Shape | What it costs |
|---|---|---|
| **A** | **A verbatim-migrated body is out of check 37's scope**; the check applies to documents authored from a template after the standard lands. | Needs a durable, checkable marker for "migrated verbatim" that a later author cannot inherit by accident. 284 documents leave the check's scope on day one. |
| **B** | **Reconcile each template's declared body shape with the shape those documents are actually written in.** | Twelve families' templates re-derived from a real corpus; the required sets stop being aspirational. Larger, and it is an amendment to W37-1's templates. |
| **C** | **Accept the 284 reds across the window** and backfill by family afterwards. | The maintainer already declined a red gate across the window for 95. This is 284. |
| **D** | **Check 37 keeps jurisdiction and W37-6 backfills all 284 bodies inside the irreversible commit.** | Puts 284 body rewrites into the one commit every precondition slice so far existed to keep work out of. |

### Recommendation — the planner's, concurring with the executor's and the lead's

**Rule the prior question rather than pick from F90's four.** The executor who measured it
recommends this, the lead concurs, and this document's own §D1 evidence is why: the four
options were each priced against a single missing section, and against the measured table none
of them reaches green. **The planner's reading is that A is the answer and B is the work it
implies** — A can be decided today and unblocks the run; B is a W37-11-sized reconciliation
that A does not depend on. **No option is adopted here.**

**One remedy is strictly safe and can be taken with or without D1, if a remedy is wanted
first**: an **asymmetric detector plus ordinal tolerance** — derive the required set from the
template at `##` exactly as now, scan the document at any depth and tolerate a leading `N. `
ordinal. Verified by running `required_sections` for every family both ways: **all twelve
required sets stay byte-identical**, so it changes no family's obligations and can only turn a
red green. **It turns no document green today** — it makes the `Acceptance` section detectable
on the 30 rulings written to comply, and those documents stay red on the three absent sections.
It is worth having because it is the piece that carries no cost; it is **not** a discharge of
F90. The symmetric variant of option 4 is the one to avoid: it newly requires a *template
placeholder* of the `slice` and `work` families (`SL-NNNNN — <Title>`, `WK-NNNNN — <Title>`), a
latent trap measured as harmless only because the migrated corpus holds zero documents of
either family.

> **Decision:**
>
> **Date:**

---

## D2 — Does the F90 slice, as ordered on 2026-09-02, still stand?

### The order, quoted

From [`…-second-withholding-and-standing-rules.md`](../rulings/RL-00976-w37-6-withheld-a-second-time-and-five-standing-rules-on-method-the-maintainer-s-2026-09-02.md)
§2.2, the maintainer's own words:

> *"F90: the red gate across the window is not accepted. The slice is cut. A depth-agnostic
> `check_shape` changes ten families and gets its own proof. It lands before the run, so the 95
> rulings the run creates are green on creation."*

…and in the superseding sequence of that record's §5, item **(b)** is *"the F90 slice — a
depth-agnostic `check_shape` with its own broken-input proof"*, made independent of (c) and
placed before the run.

### Why it is put back

**The order's stated purpose cannot be met by the remedy the order names.** A depth-agnostic
`check_shape` is measured at 95 → 95 (D1), so the 95 rulings the run creates are **not** green
on creation, and the 284 the run creates across six families are not either. The refusal of a
red gate stands untouched; what has failed is the belief that option 4 would prevent one. **No
slice was cut on this instruction, and this document is the reason it was not.**

### The options

| | Shape |
|---|---|
| **1** | **The slice waits on D1** and is re-cut against whatever the prior question rules. |
| **2** | **The slice is cut now for the safe piece only** — the asymmetric detector plus ordinal tolerance — with its own broken-input proof, understood not to discharge F90 or to prevent the red gate. |
| **3** | **The order is withdrawn** and F90's whole disposition folds into D1. |

**The planner's reading: 1, with 2 available in parallel because it costs nothing and blocks
nothing.** **Cutting a slice is the lead's**; what is reserved here is whether the *instruction*
to cut this one, and its stated purpose, are re-issued, amended or withdrawn — and, if the run
is authorised before D1 is discharged, whether a red gate across the window is accepted after
all, which is the maintainer's alone because it is a degraded repository state.

> **Decision:**
>
> **Date:**

---

## What this record does not do

It does not authorise the W37-6 run; that is the re-ask's blank maintainer's-line section and
nothing here substitutes for it. It does not amend `CLAUDE.md`, `docs/_templates/`, or
`docs/findings/FD-01027-check-37-reds-on-95-of-95-post-migration-rulings-unconditional-on-the-flag-day-because-its-section-detector-cannot-see-a-level-heading.md` — F90's amendment is PR #656's and is unmerged at `796cd07`, which
is why every figure above is cited to that PR rather than to `main`. It does not cut a slice.
