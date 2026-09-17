---
id: RL-982
family: ruling
title: the phase report's findings element is phase-scoped from the register; project-wide is a defect, not correct behaviour
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-02
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-02-w37-field-set-and-rollup-rulings.md
---

## RL-982 — the phase report's findings element is phase-scoped from the register; project-wide is a defect, not correct behaviour

### 1. Verified first, at `f226891`

The reported defect is that `FD` is absent from §1.5's applicability comments for `phase:`
(*"every WK, SL, PL, LG, RL, CR, RS"*) and `work:` (the same list), so §1.10(c)'s *"findings
opened vs discharged and the unowned-decay count"* cannot be scoped from header fields alone.
`scripts/doc-index.py` at `1c487b8` therefore reports the element project-wide and labels it so.

| Claim | Verdict |
|---|---|
| `FD` is absent from both applicability lists | **Confirmed**, in RFC-937 §1.5 and identically in the verbatim lift at `docs/process/document-ids.md` §1.5 |
| W37-1's `docs/_templates/FD.md` bars both fields from the essay | **Confirmed** — *"`kind:`, `phase:`, `work:`, `slice:`, `plans:`, `supersedes:` and `superseded_by:` do not apply to this family and must not appear here"* — and, given RL-981's carrier finding, **correct**. The essay is not where a finding's placement lives |
| The scoping information does not exist | **Refuted, and quantified.** `docs/findings/register.md` at `f226891` has **67 data rows; 67 of 67 carry a Phase cell and 56 of 67 carry a Work-item cell**, counted by an `awk` over the table that begins `\| Finding id \| Concerns \| Work item \| Phase \| Decision \|`. A second register, `docs/findings/register.md`, holds 25 rows. Every finding in this repository is already scoped to a phase, today, before any migration |
| The note carries that scoping forward | **Confirmed.** §5.2: *"the phase register's rows merge in with `phase: P1b` (RFC-756: no second copy); **per-phase views come from `doc-index.py --phase`**"*. §5.5's row for `register-lint.py` / `register-owed.py` names *"`WK-`/`SL-` in the Work-item column"* as surviving work |
| §1.10(c) can be satisfied project-wide | **Refuted by §5.4.** The `phase-review` skill's row reads *"runs `doc-index.py --phase P<n>` and reads the generated report (**which is also the phase's register view**)"*. A per-phase register view whose findings element is project-wide is not a view of that phase's register; it is the whole register with a label |
| So the report must read the essays | **Refuted.** The essays carry no placement and, under RL-981, no disposition either. The register row carries both. The report reads the register |
| The unowned-decay count is derivable from an absent `decision:` | **Refuted, and it reads zero by construction after migration.** `doc-index.py` at `1c487b8` computes it as `status == "active" and not extra["decision"]`. The register's own header prose at `f226891` requires the opposite: *"A Decision cell opens with one of ..."* — every row has one — and *"Every row carries one of the five ownership shapes: workstream, event, trigger, next-toucher, unowned-pending-authorisation."* Unowned is an **ownership shape inside the disposition**, not an absent disposition. §5.2 migrates the existing Decision cell into `decision:` unchanged, so after W37-6 the predicate matches nothing and the count is a permanent, silent zero |
| Project-wide is right for the decay count specifically | **Partly — and this is the one place the executor's instinct was sound.** The register's prose: *"Absent a named event it decays to the next `CLAUDE.md` §14 plan review, which must give it a disposition rather than merely list it."* An unowned row from an earlier phase does not stop being the next review's problem. That is a **carry-in**, reported as its own labelled figure, not a reason to leave the phase's own count unscoped |

### 2. Ruled

**Chosen: a defect, fixed in implementation. `doc-index.py --phase P<n>`'s findings element is
derived from `docs/findings/register.md` and scoped by the row's own `phase:`.** No field is
added to any family, no template changes, and §1.5's applicability comments stand exactly as
written — because they govern the essay's header, and the essay was never the carrier for a
finding's placement. Three figures, each labelled with what it counts:

- **opened in P\<n\>** — register rows with `phase: P<n>`.
- **discharged** — of those, rows whose `status:` is `closed` or `retired` (§1.2a: `closed`
  covers *resolved*; `retired` is §1.6's outcome for `decision: accept`).
- **unowned-decay** — of those, rows still `active` whose disposition names no owner and no
  event, **plus a separately labelled carry-in** of rows still `active` and unowned whose
  `phase:` is earlier than P\<n\>. Two numbers, never summed into one.

**Rejected: accepting the project-wide figure with its label.** The label is honest and the
number is still wrong for the use §5.4 names. A phase review reading *"findings opened: 87"*
learns nothing about the phase it is reviewing, and the figure grows monotonically forever.
Honesty about a number's scope does not make it the number that was asked for.

**Rejected: adding `phase:` and `work:` to the `FD-` essay header.** It contradicts §1.5's own
applicability comment, and §1.5 is the maintainer's text — that route would have gone back to
the maintainer, not been ruled here. It also duplicates what the register row holds, which is
the failure mode §5.2 flags in the same sentence.

**Rejected: deriving a finding's phase from its `created:` date against the phase sections'
`opened:` dates.** `docs/_templates/PHASE.md` does carry `opened:` and `target:`, so this is
constructible — and it was my own first answer before I read §5.2. It is wrong because it
invents a derivation the note does not state while a **stated, already-populated** field sits
in the register, and because a finding's phase is not always the phase it was written in: 67
of 67 rows at `f226891` carry a Phase cell that someone set deliberately, and 11 of them name
no work item at all. A date bucket would silently overwrite that judgement.

**Rejected: keeping `not decision` as the unowned predicate.** It is not merely imprecise; it
is a zero by construction the moment §5.2's migration fills every `decision:` — the exact
shape of failure [`RFC-789`](../rfcs/RFC-00789-zero-calls-above-200k-tokens-measures-the-compaction-cap-not-discipline.md)
records, where a boundary metric reads zero because of where the boundary sits rather than
because the population is empty.

**The mechanism, in three parts.**

1. **One source, named.** The findings element reads `docs/findings/register.md` and nothing
   else. The essays are not consulted for it, so the essay/row divergence RL-981 leaves
   possible cannot reach a reported number.
2. **Coverage is asserted, not inferred.** The count of rows the parser accepted must equal the
   count of data rows in the file, and the report fails loudly when they differ. A register
   whose table shape changes must break the report, not quietly shrink it.
3. **The unowned predicate is stated in the register, tested against a positive control.** The
   ownership shapes are the register's own five; whichever spelling W37-6's rewritten header
   prose fixes on, the test corpus must contain at least one row that the predicate matches and
   at least one it does not, so the number can never be trusted merely because it is small.

### 3. What it obliges

- **W37-3** replaces the project-wide element and its label with the three scoped figures, and
  points the derivation at the register. Its module docstring's second *"interpretation this
  module makes where RFC-937 is silent"* is retired and replaced by a citation to this ruling —
  the note was not silent; the statement was in §5.2 and §5.4 rather than §1.5.
- **W37-4** builds check 33's register-row checks against the same field set, and the
  broken-input proof for the coverage assertion.
- **W37-6** rewrites the register's header prose (§5.2) so the row's fields, including the
  unowned ownership shape, are declared in one place.
- **Nothing in RFC-937 or `document-ids.md` is edited**, and no template gains a field.

### 4. Acceptance — the violation that must become detectable

1. **Unscoped.** A fixture register with rows in two phases, reported with `--phase P2`, must
   count only P2's rows as opened. **Violation: the opened count equals the register's total
   row count** — the project-wide symptom, stated as the thing that must red.
2. **Silently empty.** **Violation: the report renders with a parsed row count lower than the
   register's data-row count, and still exits 0.** A register the parser cannot read must break
   the report; it must not produce a smaller, plausible number.
3. **The zero-by-construction predicate.** A fixture register in which **every** row carries a
   `decision:` and exactly one names no owner must report unowned-decay `1`. **Violation: it
   reports 0** — which is precisely what the `not decision` predicate returns on that corpus,
   and what it will return on the real corpus after W37-6.
4. **Lost carry-in.** A fixture with an `active`, unowned row in P1b, reported with
   `--phase P2`, must show that row in the carry-in figure. **Violation: it appears nowhere in
   the report** — the register's own decay rule dropped on a phase boundary, which is the one
   place it exists to survive.

---
