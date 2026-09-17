---
id: RL-910
family: ruling
title: Q2: RL-906's mechanism does not transfer, its principle does, and the answer here is to conform the corpus and red-gate from day one
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-30
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-30-nt-0015-q1-q5-rulings.md
---

## RL-910 — Q2: RL-906's mechanism does not transfer, its principle does, and the answer here is to conform the corpus and red-gate from day one

### 1. Verified first, at `01ba0bd`

| Claim | Verdict |
|---|---|
| RL-906 ruled the same *shape* of question | **Confirmed** — [`RL-00908-impact-matrix-row-4-does-not-sit-forever-it-inverts-and-part-c-row-5-closes-here.md`](RL-00908-impact-matrix-row-4-does-not-sit-forever-it-inverts-and-part-c-row-5-closes-here.md) RL-906, on whether a new check red-gates records predating it |
| RL-906's mechanism was a filename date against a constant cutoff | **Confirmed** — *"the discriminator is a fact in the file — its own filename date, compared against a cutoff date written as a constant in the check"* |
| RL-906's reason was that its corpus may not be edited | **Confirmed** — *"reddening 114 frozen records would force either an edit to a record (forbidden) or a permanently-ignored gate"*, resting on `docs/plans/README.md`'s *"Do not edit a filed plan to agree with today's repository"* |
| register rows carry no per-row date | **Confirmed** — the five columns are Finding id, Concerns, Work item, Phase, Decision. No date column exists; dates appear only inside amendment prose |
| register rows conform to the note's four decision shapes | **41 of 51 do; 10 do not** — measured by matching each Decision cell's opening against `carry forward` / `accept —` / `fix before close —` / `split verdict` |
| `CLAUDE.md` §13's four verdicts already appear in the Decision column | **Confirmed** — F53 opens `**delivered but untested**`, F54 opens `**not started**` |

The 10 non-conforming rows, by class:

| Class | Rows | What it is |
|---|---|---|
| status written into the Decision cell | F-W10-1-1, F-W10-2-1, F-W10-2-2, F32, F28 | `resolved <date> …` or `Fixed —` where a disposition belongs. Dissolved by P4's separate status field; not a grammar gap |
| `CLAUDE.md` §13 verdicts | F53, F54 | `delivered but untested`, `not started`. §13 is binding and outranks the register's local vocabulary; the **grammar** is short, not the rows |
| negated shape | F37, F40 | `fix before close is not available` / `is not required` — a real decision the four shapes cannot express |
| table defect, not vocabulary | F27, F49 | literal `\|` inside inline code, splitting the rows into 7 and 6 fields. F49's Decision cell currently reads as a fragment of a shell command |

### 2. Ruled

**RL-906's mechanism does not transfer, and neither does its conclusion. Its principle
does, and it is the part that was doing the work.**

- **The mechanism fails for want of an analogue.** A register row is a line in one
  continuously-amended file. It carries no filename, no date field, and no durable fact
  saying which side of any cutoff it was written on. A date parsed out of amendment prose
  would be a fact about the row's *last edit*, not its origin — `CLAUDE.md` §13's
  name-the-range-not-the-tip failure in miniature.
- **The conclusion fails because its premise is inverted.** RL-906 never red-gated legacy
  plans because editing them is *forbidden*, which left only a permanently-ignored gate.
  Editing a register row is the register's **normal operation** — 16 commits today, 7 rows
  carrying in-place resolution annotations. The dilemma that forced RL-906's hand does not
  exist here. There is a third option it did not have: **fix the records.**
- **The principle transfers intact, and it is what kills the note's proposal.** *A verdict
  must be a property of the artifact, not of when the check runs.* Q2's recommended
  "warn-then-red with a dated flag-day" makes the identical register pass on Tuesday and fail
  on Wednesday with no content change, and no fresh clone can reproduce a verdict. Rejected
  for exactly the reason RL-906 rejected it — the reasoning is general even though its
  remedy was specific.

**Ruled: no legacy class, no exemption, no warn phase, no flag day. The corpus is conformed
in the RL-909 PR, and `register-lint.py` is red on the first day it lands, on every row.**
Four parts:

- **The residue is 10 rows, not 51**, and the four classes above make each a bounded edit.
  The class that looks largest — status in the Decision cell, 5 rows — is not a grammar
  question at all and disappears when P4 gives status its own field.
- **The grammar P1 specifies is the union**, not the note's four shapes: the register's own
  disposition vocabulary *plus* `CLAUDE.md` §13's four verdicts, which are binding, already
  present, and may not be linted away. A grammar that reds F53 and F54 would be a register
  check overruling `CLAUDE.md`.
- **The two pipe-broken rows are fixed as a defect, before any lint exists.** They are not
  legacy style; they are rows a five-column parser cannot read today, and the register is
  the artifact `scripts/audit-docs.py` check 25 resolves every finding citation against.
- **P3 lands after the RL-909 PR, never before.** RL-906's *"the check and the format
  it validates land in the same commit"* becomes here: the check lands after the corpus
  already parses, so day one has zero exempt rows and the check can still fail — which is
  `CLAUDE.md` §13's *"a check that has never printed a failure has not been tested"*.

**Scope is the live register only.** `docs/findings/register.md` — the one archived
phase register that exists, 96 lines — is **excluded by name, not by date**: it belongs to a
closed phase and is a record, and the note's own "deliberately unchanged" list already holds
closed records outside this work. A phase-2 register is in scope from the commit that creates
it. Naming the exclusion keeps it visible; a date-shaped exclusion would reintroduce exactly
what this ruling rejects.

### 3. What it obliges

RL-909's PR does the conformance. The P3 slice writes `scripts/register-lint.py` with no
cutoff constant of any kind. §13's proof needs three deliberately broken fixtures, each named:
a row whose Decision parses to no shape in the grammar; a row with a resolution annotation
carrying no date and no PR or SHA; and an unowned row naming no decay event. Plus the control
without which the check can go green by exempting everything: **the live register at the tree
the check lands on must pass**, reported with that tree.

**Overridden if** `register-lint.py` contains a cutoff date, a warn level, or any per-row
exemption; if it lands before the RL-909 PR; or if the grammar it enforces excludes
`CLAUDE.md` §13's four verdicts.

---
