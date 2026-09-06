---
id: RL-905
family: ruling
title: Q1: the extract stays hand-maintained, and that is only defensible if the gate can tell when it has fallen behind
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-30
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-30-nt-0014-q1-q3-q4-rulings.md
---

# RFC-895 Q1, Q3 and Q4, and the disposition of impact-matrix row 4 (2026-08-30)

**What this is.** The remaining three of RFC-895's four open questions, ruled at step 2 of
the note's own adoption workflow, plus the disposition of the one impact-matrix row whose
trigger [RL-920](RL-00921-a-ref-may-not-be-served-from-the-memo-without-a-metadata-read-and-it-does-not-need-to-be-the-content-hash-is-already-in-hand-after-the-first-read-and-is-discarded.md) dissolved.
Q2 was ruled there. The questions are in
[`../rfcs/RFC-00895-a-machine-readable-core-for-the-delivery-process-so-the-rules-a-script-can-check-stop-being-prose.md`](../rfcs/RFC-00895-a-machine-readable-core-for-the-delivery-process-so-the-rules-a-script-can-check-stop-being-prose.md)
§7; the slices they gate are E, F and G of
[`../plans/PL-00899-rfc-842-rfc-843-rfc-895-adoption-plan-delegation-and-rulings.md`](../plans/PL-00899-rfc-842-rfc-843-rfc-895-adoption-plan-delegation-and-rulings.md).

**Each question arrived carrying a proposal. Two of the three proposals are ruled down in
their mechanism** while their conclusion is kept — a note proposes and decides nothing
([`../rfcs/README.md`](../rfcs/README.md)), and adopting a proposal
because it is the only text on the table is how an unexamined default becomes governance.

**Numbering continues at 45, 46, 47, 48.** Verified rather than relayed: every `## Ruling N`
heading under `docs/plans/` at `1407e09` yields exactly 44 rulings, numbered 1–44 with no
gap and no duplicate. 44 is
[`RL-00916-the-field-is-the-environment-the-quote-was-served-in-the-spec-already-says-so-and-the-branch-does-not-merge-until-it-says-so-too.md`](RL-00916-the-field-is-the-environment-the-quote-was-served-in-the-spec-already-says-so-and-the-branch-does-not-merge-until-it-says-so-too.md).

**This record makes no edit to any other document.** Every ruling below names the document it
obliges and who writes it. `docs/process/delivery-process.md` is not `docs/specs/`, and the
decision-maker charter's write scope does not reach it; the sentences ruled in Rulings 45 and
48 are specified here verbatim and land in the adoption's next slice, written by the executor
under the lead.

---

## RL-905 — Q1: the extract stays hand-maintained, and that is only defensible if the gate can tell when it has fallen behind

### 1. Verified first, at `1407e09`

| Claim | Verdict |
|---|---|
| C4 exists and has been running since slice B | **Confirmed** — `scripts/audit-docs.py` check 26, merged `0be9c3c` (#451) |
| check 26 compares the extract's content against the markdown | **False, and it says so itself.** It resolves `source` § citations, and asserts `meta.authoritative is false` and that `meta.derived_from` is a file (`scripts/audit-docs.py:533-655`). Its own docstring: *"This is the cheap half of a drift check … A citation that resolves is not proof the cited text still says what the citer thinks"* |
| a generator for the extract exists | **No** — no such script in `scripts/`; the extract is hand-written and has exactly one commit, `33b5ef1` |
| the process spec claims more enforcement than exists | **Yes** — §10's bullet reads *"a drift check compares the two (RFC-895 §3)"*. Nothing compares the two |
| the extract has fallen behind its source | **Yes, measurably.** `delivery-process.md` has two commits after the extract's only one (`2e4684b`, `97965be`); `97965be` added two normative rules to §15, the section `guards.message_discipline` cites. The extract was not revisited, and the gate was green throughout |
| `meta.verified_against_tree` | Reads `6f77abb` — a tree **older than the extract's own filing commit**, which itself changed `delivery-process.md`. The stamp was stale on arrival and nothing can see it |

### 2. Ruled

**Hand-maintained, not generated** — the note's answer, for a reason the note does not give.
There is no second machine-readable source to generate *from*. Generating would mean
embedding the values in the markdown, which is the prose-to-JSON migration the note's own §4
rules out, and would make the markdown worse at the one job
[`../../CLAUDE.md`](../../CLAUDE.md) §15 gives it: *"read the markdown to know the process"*.
This is **not** the `docs/contracts/` pattern; that one has `model-schema`, a formal source
a generator can read. Here the source is prose, and a "generator" would be a parser of
English pretending to be a build step.

**But hand-maintained is adopted with a condition, and the condition is the ruling.** The
extract records a digest of the exact bytes of `meta.derived_from`, paired with the commit
that digest was taken at, and a new `audit-docs.py` check fails when the digest and the file
disagree.

- **Without it, "hand-maintained and drift-checked" means "unmaintained, with a citation
  checker".** That is the state on disk right now, and the two-commit lag above is what it
  produces: the only mechanism that would have made anyone open the extract is one that reds
  when the source moves.
- **The digest is the whole of the mechanizable half.** Comparing prose to JSON semantically
  is not buildable; comparing "the source has not moved since a human last reconciled the
  extract against it" is three lines and is the check that actually forces the reconciliation.
  It is `generate-contracts.py --check` semantics applied to a hand-maintained artifact.
- **The pairing with a commit is not decoration.** A bare digest failure says only "it
  changed"; the recorded commit lets the failure message name the exact range to read —
  `git diff <recorded-commit>..HEAD -- docs/process/delivery-process.md` — which is the
  difference between a session re-reading the diff and a session bumping a hash. It also
  makes `verified_against_tree` load-bearing for the first time: today it is a field nothing
  can falsify, which is the failure RL-907 rules on one artifact later.
- **Known cost, accepted:** the check reds on every edit to the process spec, including a
  typo. The spec has twelve commits in its life. That is the right price for a forced re-read.

**Two consequential clauses.**

- **§10's sentence is amended to describe the checks that exist**, replacing
  *"and a drift check compares the two (RFC-895 §3)"* with: *"Two gate checks hold it to
  that: every block's citation must resolve in this document, and the extract must record
  the digest of the revision of this document it was last reconciled against, so a change
  here reds until someone re-reads it."* A spec asserting an enforcement the repository does
  not have is `CLAUDE.md` §0's spec-and-code disagreement, and the spec is the wrong side.
  **`CLAUDE.md` §15 carries the same overstatement** — *"a drift check fails the gate when
  they disagree"* — and is **not ruled here**: amending that file is the maintainer's (§12).
  It is named so that fixing §10 alone does not leave the stronger claim standing in the
  more-read document, which is how a corrected sentence survives its own correction.
- **The extract's `meta.note` states that its blocks are the mechanically-checkable subset
  of their section, not an exhaustive rendering.** `guards.message_discipline` carries four
  constants while §15 now carries more rules than four, and nothing on the artifact says
  whether that is extraction or omission. Unmarked, a reader takes the extract's silence for
  the spec's silence — which is the one reading the authority rule was written to prevent.

### 3. What it obliges

The digest field, the new check, §10's sentence and the `meta.note` sentence land together;
the lead cuts them into slice F or a slice of their own. The check goes **inside**
`scripts/audit-docs.py`, by RL-920 §2's test — the state is written down in a file, so a
check can verify it — taking the next free number at the time it lands (27 is free at
`1407e09`). §13's broken-input proof: one byte changed in `delivery-process.md` reds it, with
a negative control changing a different file that must stay green.

**Overridden if** the check lands as a separate script, if the digest is taken over anything
but the exact bytes of `derived_from`, if the commit pairing is dropped, or if §10's sentence
stands as written.

### 4. Was this already settled *de facto* by slice B?

**Half of it, and the half that matters was not.** Slice B settled *where* the check lives
and made the "generated" branch unattractive by shipping nothing to generate. It did not
settle Q1, because Q1's proposal is "hand-maintained **+ C4**", and the C4 that exists cannot
observe the drift the proposal relies on it to observe. Reporting Q1 as settled would have
booked an enforcement the repository does not have — and the evidence the lead expected to
find in C4's run history is real, but it points the other way: the check ran green across two
commits that put the extract behind.

---
