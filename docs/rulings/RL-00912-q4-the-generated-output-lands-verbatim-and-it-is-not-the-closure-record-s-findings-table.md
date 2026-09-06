---
id: RL-912
family: ruling
title: Q4: the generated output lands verbatim, and it is *not* the closure record's findings table
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

## RL-912 — Q4: the generated output lands verbatim, and it is *not* the closure record's findings table

### 1. Verified first, at `01ba0bd`

| Claim | Verdict |
|---|---|
| a closure record's findings list is a `CLAUDE.md` §14 requirement | **Confirmed** — [`../closures/CR-00927-work-item-record-wk-671-scoring.md`](../closures/CR-00927-work-item-record-wk-671-scoring.md) §6: *"`CLAUDE.md` §14 requires every open finding to be listed here with its resolution"* |
| that list is a transcription of register rows | **No.** WK-671 §6 has 11 entries. Four name findings with no register row at all (`NFR-489 fails at the full path`, `NFR-502 owed, not delivered`, `FR-RATE-36, 37, 42 not started`, `NFR-500 not started`); one is not a finding (`The §14 plan review — runs with this close`); and every entry's Resolution column is a judgement written **for that close**, not the register's Decision |
| the failure Q4 answers is a completeness failure | **Confirmed** — F41, verbatim: the owed list *"already runs to thirteen items — a list that lost NFR-502/501 for two workstreams even though a register row, F-W9-1, existed for them the whole time"* |
| the close checklists mention an owed list today | **No** — the string `owed` appears in neither `docs/process/checklists/work-item-close.md` nor `phase-close.md` |
| the register is stable enough to cite by command alone | **No** — 16 commits on 2026-08-30; the same command run a day later returns a different list |

### 2. Ruled

**Verbatim — Q4's recommendation is adopted in its conclusion, and its rationale is
sharpened.** The note's ground ("the record should survive the script changing") is true but
understates it: a closure record is frozen and the register is amended several times a day, so
a command-plus-tree citation to a mutable file records a claim no later reader can reproduce
without checking out that tree — the dated-absence-claim failure, and a breach of
`CLAUDE.md` §13's *"a reference carries its scope and its measurement"*. **A citation-only
answer is ruled out.**

**But the output is not the §6 table, and this is the half Q4 does not ask.** Measured above,
§6 is not a list of register rows: nearly half its entries have no row, and every entry
carries a per-close judgement the register does not hold. Pasting a generated block in as §6
would either delete those judgements or stand a second list beside them — `RFC-756`'s
duplicated-status failure inside the closure record.

**Ruled: `register-owed.py`'s output lands verbatim in the closure record as a fenced,
explicitly-generated evidence block, and §6 stays hand-written.** The block's job is to make
§6's completeness falsifiable, which is precisely F41's failure and nothing wider. Three
constraints:

- **The block names the command, and the committed revision it ran against** — a SHA on
  `main` or a named branch range, never a dirty worktree and never a bare date, because the
  register at a date is not a resolvable object.
- **The record states the reconciliation in one sentence**: every id in the block appears in
  §6 with a resolution, and §6 adds nothing the block does not carry unless that addition is
  named as a finding with no register row. That sentence is what discharges F41; a block
  nobody reconciles against is decoration.
- **The block is evidence, not authority.** Where the generated list and §6 disagree, §6 is
  amended or the register is — never silently either, per `CLAUDE.md` §0.

### 3. What it obliges

The P5 slice, plus the two close checklists, which currently say nothing about an owed list
at all — so this is an addition to both, not an amendment of an existing step. Text in
§Text specified for others.

**Overridden if** the generated block replaces or duplicates the §6 resolutions table, if it
cites a date or an uncommitted tree instead of a revision, or if the reconciliation sentence
is omitted — in which case the record carries a list nothing checks, which is where F41 began.

---
