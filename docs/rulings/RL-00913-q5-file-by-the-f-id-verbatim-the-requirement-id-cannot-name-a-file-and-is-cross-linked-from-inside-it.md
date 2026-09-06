---
id: RL-913
family: ruling
title: Q5: file by the F-id, verbatim; the requirement id cannot name a file and is cross-linked from inside it
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

## RL-913 — Q5: file by the F-id, verbatim; the requirement id cannot name a file and is cross-linked from inside it

### 1. Verified first, at `01ba0bd`

| Claim | Verdict |
|---|---|
| a requirement id uniquely identifies a row | **No** — `FR-231` appears in the first column of **two** rows: `FR-231/233/234/235 (F-W10-1)` and `FR-231 (F-W10-2)` |
| every row names a requirement id | **No** — `03 rating surface (F8)`, `.claude/roles/`+`.claude/skills/` CI gap (F26), and every row filed since F49 open with a prose phrase and no requirement id |
| a row names at most one requirement id | **No** — F22's Concerns cell enumerates roughly sixty ids across three phases |
| F-ids are unique and permanent | **Confirmed** — `docs/findings/register.md`'s F42 tombstone note: *"the register's finding ids are held to the same rule: never renumber, never re-use; append, mark superseded, or leave a tombstone"*, citing `CLAUDE.md` §5 |
| the F-id namespace is already machine-defined | **Confirmed** — `scripts/audit-docs.py`'s `_FINDING_ID` regex, described there as *"the findings register's own id shape, confirmed against every row"*; it admits exactly `F<n>` and `F-W<n>-<n>` with an optional third segment |
| F-ids are globally unique across the repository | **No** — check 25's docstring records the register's F13 (`FR-25`) colliding with `docs/research/track-a-findings.md`'s own local F13 (`FR-129`). Uniqueness holds **within the register**, which is why the directory namespace matters |

### 2. Ruled

**`docs/audit/findings/<F-id>.md`, the F-id written exactly as the register writes it** —
`F27.md`, `F-W9-3.md`, `F-W10-1-1.md`. The requirement id is cross-linked from inside the
file and stays in the row's Concerns column, where it already is.

The reason is not preference: **the requirement id cannot be a filename here.** It is not
unique (FR-231 names two rows), not always present (three row shapes carry none), and not
singular (F22 carries about sixty). Every one of those three is disqualifying on its own. The
F-id is the only identifier the register guarantees is one-per-row, permanent, and already
parsed by a gate.

Three sub-rules, each closing a way this drifts:

- **A file name is exactly `_FINDING_ID`.** No suffix, no slug, no description. A filename
  that carried the concerns phrase would go stale the first time the phrase was amended, and
  the register amends daily.
- **Limbs never mint a filename.** F27's `(c)`, F43's L1/L2/L3, F45's `(i)`/`(ii)` are
  sections inside one file, never `F27c.md`. Minting `F27c` would create an id outside the
  namespace `CLAUDE.md` §5 and the F42 tombstone hold closed.
- **The row keeps naming itself `(F27)`.** P4 must not replace the parenthesised self-naming
  with a bare id or a link title: `scripts/audit-docs.py` check 25 resolves every finding
  citation in `docs/plans/`, `docs/research/` and `.claude/notes/` by matching that exact
  form against this file. Verified as a **non-impact** provided the index row survives — the
  note's impact matrix does not mention `audit-docs.py`, and it would become an impact the
  moment P4 moved a row instead of shortening it.

### 3. What it obliges

The P4 slice, and the `docs/audit/findings/README.md` the impact matrix already names, which
states this rule and the row-to-file link direction.

**Overridden if** any findings file is named by a requirement id, by a slug, or by a limb
id, or if P4 changes how a register row names itself.

---

## Dispositions of two impact-matrix rows

**Row 13, `docs/open-questions.md`** — *"§7 questions on filing"*. **Discharged as not
required, here.** `docs/open-questions.md` mirrors `docs/specs/` open questions under the
`OQ-<MODULE>-<n>` namespace, and RFC-896's five questions are neither spec questions nor open
any longer. Raising five OQ ids and resolving them in the same day would put five permanent
ids into a namespace `CLAUDE.md` §5 never lets anyone reclaim, to record something this
record already holds. Row 13 is struck.

**`docs/audit/phases/*/register.md` is missing from the impact matrix.** One exists
(`docs/findings/register.md`, 96 lines) and the work-item close checklist requires a
carried finding to be copied to both it and the global register. RL-910 §2 excludes the
1b register by name and puts a future phase-2 register in scope from its creating commit; the
matrix should carry that as an explicit row rather than leaving a second register unmentioned.

---

## Text specified for others

Everything here is outside the decision-maker's write scope. Verbatim where quoted; the
auditor may vary wording with a stated reason, but not the constraints the rulings above set.

### A. `docs/findings/register.md` header — replaces the removal sentence (RL-909)

Replace:

> A finding is removed when the close resolves it, accepts it, or re-plans it with an owner.

with:

> A finding is not removed when it resolves. Its row is annotated in place — `**Resolved
> <date>**`, naming the PR or commit that discharged it and quoting what the annotation
> supersedes — because a deleted row leaves every citation to it dangling, and
> `scripts/audit-docs.py` check 25 resolves finding citations against this file. A row is
> removed only when the phase whose register carries it is archived.

### B. `docs/findings/register.md` header — the decay sentence (RL-909, P2)

> An unowned row must name the event that next confirms or assigns its owner. Absent a named
> event it decays to the next `CLAUDE.md` §14 plan review, which must give it a disposition
> rather than merely list it; a row that reaches a review and leaves it unchanged is a review
> finding, not a register one.

### C. `docs/findings/register.md` header — the grammar paragraph (RL-909, P1)

The paragraph must enumerate, and nothing else is a valid Decision opening:

- the disposition vocabulary the rows already use — `fix before close`, `accept`,
  `carry forward`, `split verdict` — each with its qualifiers (`with an owner`,
  `with a trigger`, `unowned`, `phase boundary`, `provisional owner`);
- **`CLAUDE.md` §13's four verdicts** — `delivered but untested`, `deferred with an owner`,
  `reassigned`, `not started` — which are binding, already appear (F53, F54), and may not be
  linted away by a register-local vocabulary;
- the negated form F37 and F40 need: a decision that a fix is **not available** or **not
  required** before close, which must state where the work goes instead;
- the five ownership shapes: workstream, event, trigger, next-toucher,
  unowned-pending-authorisation.

Status is not a Decision. The five rows that write one there (F-W10-1-1, F-W10-2-1,
F-W10-2-2, F32, F28) are corrected when P4 gives status its own field, or sooner.

### D. `.claude/skills/phase-review/SKILL.md` (RL-909 B, impact-matrix row 12)

> The agenda includes every `docs/findings/register.md` row that has decayed to this review —
> every unowned row naming no other event. Each gets a disposition in the review's output:
> an owner, an accepted deferral with a new named event, or a finding against the register.
> Listing one without disposing of it is not a disposition.

### E. `docs/process/checklists/work-item-close.md` and `phase-close.md` (RL-912)

Neither file currently mentions an owed list; this is a new step in both.

> **The owed list is generated, not recalled.** Run `register-owed.py <id>` against a
> committed revision and paste its output verbatim into the closure record as a fenced block
> marked generated, naming the command and that revision. The block is evidence; the record's
> own findings-and-resolutions table stays hand-written, because it carries per-close
> judgements and findings that have no register row. State in one sentence that every id in
> the block appears in that table with a resolution, and that the table adds nothing the block
> does not carry except findings named as having no register row.

### F. Adoption plan (RL-909)

S1 is deleted, not re-scoped: its content is the RL-909 PR, which lands ahead of the plan.
S2 (`register-lint.py`) may not land before that PR has merged.
