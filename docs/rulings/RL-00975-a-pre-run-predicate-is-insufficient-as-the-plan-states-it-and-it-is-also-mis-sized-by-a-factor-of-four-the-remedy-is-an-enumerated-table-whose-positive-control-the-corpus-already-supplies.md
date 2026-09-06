---
id: RL-975
family: ruling
title: a pre-run predicate is insufficient as the plan states it, and it is also mis-sized by a factor of four; the remedy is an enumerated table whose positive control the corpus already supplies
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-02
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-02-w37-6-leaf-plan-findings-rulings.md
---

## RL-975 — a pre-run predicate is insufficient as the plan states it, and it is also mis-sized by a factor of four; the remedy is an enumerated table whose positive control the corpus already supplies

### 1. The lead's concern is correct, and the measurement makes it concrete

The plan's §10 finding 9 and §7.5 identify the one place a wrong result passes the whole gate:
splitting `docs/closures/INDEX.md#closure-recordsmd` per heading mints a `CR-` for each record, three of
which are *"in progress, not closed"* and one of which is a phase; shape and header are both
correct, so checks 31 and 37 pass, and **no check tests whether a closure record records a
closure.** Its remedy is *"the split rule must exclude them by predicate before the run."*

The concern that a pre-run predicate is a one-time human judgement with no failing case is right.
The measurement makes it sharper than an argument could:

| `closure-records.md` at `e93e0e4` | Count | The plan's figure |
|---|---|---|
| `###` records in total | 21 | 21 |
| Work closes (`W<n> — …: closed <date>`) | **8** | implied 17 |
| Phase close (line 8, `Phase 1a — exit demo accepted`) | 1 | 1 |
| Marked `*(in progress, not closed)*` | **10** | **3** |
| Neither a close nor a slice record — line 1121 `Independent audit`, line 1555 `WK-660 mid-workstream scope findings` | **2** | not identified |
| `##` headings | 0 | 0 |

**The predicate as stated is wrong about its own population by a factor of more than three, and
misses a further category entirely.** Only 8 of 21 records are work closure records. A predicate
written to exclude three would have left **seven** documents in the tree asserting closures their
sources do not record. That is not a hypothetical failure mode of the predicate approach; it is
the actual state of the predicate the plan proposes.

### 2. Ruled

**A pre-run predicate is not sufficient — but not because predicates are wrong. It is
insufficient because the plan states no expected output for it.** A predicate whose result is
never compared against an independently-stated expectation is a private judgement; the same
predicate whose output is asserted against a stated set is a test with a failing case. The
distinction is the whole of `CLAUDE.md` §13's *"a check that has never printed a failure has not
been tested"*, and the evidence that it bites here is that the unasserted figure was wrong.

**Three parts.**

1. **The split is driven by an enumerated table, not a predicate.** W37-6's ledger carries a
   **21-row table**, one row per `###` heading, giving its line number, its verbatim heading text,
   and its destination family and `kind:`. A table can be read and disagreed with by someone who
   was not there; a predicate cannot.
2. **Nothing is excluded.** Acceptance (g) class 4 requires the outputs' concatenation to
   reproduce the input's body lines in order. Excluding thirteen records is thirteen blocks of
   body lines with no output — either a (g) failure or a carve-out in (g), and a carve-out in (g)
   is what [RL-989](RL-00990-rfc-937-1-5-s-vendored-parenthesis-is-a-gloss-not-a-detector-the-set-is-declared-and-reconciled-and-the-exemption-reaches-only-the-blanket-passes.md) closed. Each record gets
   a destination; **a record that is not a close does not become a `CR-`.**
3. **`CR-` cannot express "not closed", and this was checked rather than assumed.** RFC-937 §1.2's
   `CR` row is *"one work, phase or review close"*, mutability *write-once*, status subset
   **`active`** — a single value, with no non-closed member. So the ten in-progress records and
   the two non-closure records are **not `CR-` documents at all**; only the 8 work closes and the
   1 phase close are, the latter as `kind: phase`, which the family already carries. **Which
   family the other twelve take is the planner's derivation under §5.2's own rules, not this
   ruling's** — this ruling fixes that they may not be `CR-`, and that they may not be dropped.

### 3. Why this answers "must something detect it after the fact?" — yes, and two things can

The lead asked whether something must be able to detect the failure after the run. It must, and
the migration's own output supports two independent detectors, neither of which requires re-running
the predicate:

- **Count-facing, readable from the artifacts alone.** After the run, exactly **9** documents
  derived from `closure-records.md` are `CR-` (8 `kind: work`, 1 `kind: phase`), and all 21
  headings have a `REDIRECTS.csv` row. Anyone can check this later without any of the executor's
  context.
- **Check-facing, with a positive control the corpus already contains.** A `CR-` whose body
  carries an in-progress marker is a violation, and the ten marked records are ten real inputs on
  which such a check can be proven to fire. **This is the argument against exclusion that matters
  most:** excluding them removes the only true positives the repository has for this class, and a
  check written afterwards would have nothing to be tested against. RL-988 acceptance item 2's
  standard — *"a control that runs a different regex body goes green because of what it misses"* —
  applies to the population as much as to the pattern.

### 4. Acceptance — the violation that must become detectable

1. **The predicate's output is asserted, not trusted.** Before the split, run the in-progress
   predicate over `closure-records.md` and compare its output to the ten line numbers named in §1
   above. **Violation: it returns three (the figure the plan states), returns any of the eight
   work closes, or returns a count the ledger does not state in advance.** This is the item that
   converts a private judgement into a test, and it is the one this ruling exists for.
2. **The result is checkable from the artifacts after the fact.** **Violation:** the post-migration
   tree containing 21 `CR-` documents derived from `closure-records.md`, or any `CR-` whose body
   contains `in progress, not closed`, or fewer than 21 `REDIRECTS.csv` rows sourced from that
   file's headings.
3. **The same defect class must be swept, not just its reported instance.** `plan-reviews.md` has
   14 `###` of which 11 are reviews and 3 sit under `## Pending proposals` with no §5.2
   destination; the same enumerated-table rule applies to it. **Violation: a `CR- kind: review`
   minted from any of the three `Pending proposals` candidates, or any of the three dropped**
   (the marker class is swept, not the reported symbol).

---

## Acceptance Standard

This record is complete when all six of the following hold. Each is stated as a violation, per
`CLAUDE.md` §13.

1. **Every ruling number is unused.** `git grep -oh -E 'Ruling (7[3-8])' origin/main -- .` returns
   nothing at the merge base of this branch. *Violation: any of 73-78 already minted.*
2. **Every amended ruling names what it supersedes, and the superseded text is quoted.** RL-970
   quotes RL-987 acceptance item 2 verbatim before withdrawing it; RL-973 quotes RL-990
   §3's obligation before restating it. *Violation: an amendment that states a new position
   without quoting the old one — which leaves both live.*
3. **Every acceptance item in every ruling is a violation, not a description.** *Violation: an
   acceptance item that cannot fail, or that describes correct behaviour rather than the
   observation that would falsify it.*
4. **Every measured figure carries its method and its tree.** *Violation: a count without the
   command that produced it and the SHA it was produced at.*
5. **The gate is green.** `python3 scripts/audit-docs.py` exits 0 on this branch. *Violation: any
   non-zero exit — including check 28 demanding this section, which is honoured here rather than
   evaded, and check 19's `ADR-` resolution, which this record avoids tripping by citing no ADR.*
6. **Nothing outside this role's charter is decided.** *Violation: this record accepting a Work,
   Phase or Project close, amending `CLAUDE.md`, editing a frozen plan, or making a sequencing
   decision — §7 names what was referred up instead.*

---

## 7. What this record does not rule, and where each goes

| Question | Whose | Why not this role's |
|---|---|---|
| Whether W37-7 runs immediately after W37-6, with `git-hygiene` first in its order | **The lead's** | Sequencing. RL-971 removes the argument that made it urgent; it does not decide the order |
| Whether `docs/process/delivery-process.md` gains a step requiring a branch open across a ruling's merge to be re-read against that ruling before merging | **The lead's** | Process, and `.claude/roles/lead.md` names that file as the lead's to write. RL-973 §2 records the mechanism; the process change is not this role's to impose |
| Which family the twelve non-close records in `closure-records.md` take | **The planner's** | A derivation under RFC-937 §5.2's own rules. RL-975 fixes only that they may not be `CR-` and may not be dropped |
| How check 39's PR-title clause is ever enforced, given that `audit-docs.py` cannot read git or GitHub | **A later slice's decision point** | It is a new capability decision, not a W37-6 question. Raised in RL-971 §3 so it is scheduled rather than discovered |
| Whether W37-6's disclosure package is sufficient for the maintainer's go-ahead | **The maintainer's** | The delegation record §2 reserves acceptance; a go-ahead on an enlarged commit is the maintainer's to give |
| Whether the two-file divergence between 928 and 930 legacy-form carriers matters | **Deliberately unresolved** | Re-derived in the running session per the plan's own acceptance (f); this record states its own method rather than reconciling a figure whose method is unstated |

---

## 8. One thing that got caught only by reading to the end, recorded because the next reader will not

The lead's brief relayed the leaf plan's finding 12 as *"RL-987's acceptance item 2 cannot
discriminate a member from a non-member"* — true, and the plan's evidence for it is correct. What
neither the brief nor the plan reports is that the same item **fails for four real members**, one
of them a primary instrument from the map plan's own floor. The false-positive direction is the
one you find by reasoning about the test; the false-negative direction is the one you find only
by running it against the actual member list. Running it cost one script and eleven seconds, and
it changed the amendment from *"add a sharper test"* to *"withdraw this one, because acting on it
would have removed four instruments from the commit that exists to carry them."*

The transferable rule, and it is the reason this section exists rather than a note: **when a test
is reported as too weak, run it in both directions before amending it.** A test that admits too
much and a test that excludes too much are the same defect seen from two sides, and the second
side is the one that does damage.
