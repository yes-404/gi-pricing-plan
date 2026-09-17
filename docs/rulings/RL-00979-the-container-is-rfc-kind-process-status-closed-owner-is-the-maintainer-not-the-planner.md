---
id: RL-979
family: ruling
title: the container is `RFC-`, `kind: process`, `status: closed`; `owner:` is the maintainer, not the planner
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-02
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-02-w37-container-family-and-line-citations-rulings.md
---

# The `Pending proposals` container's family, and line-number citations into a split file, ruled (2026-09-02)

**What this is.** Register row 7. The planner returned
[`../plans/PL-00964-the-pending-proposals-container-its-family-and-kind-a-derivation-for-ruling-2026-09-02.md`](../plans/PL-00964-the-pending-proposals-container-its-family-and-kind-a-derivation-for-ruling-2026-09-02.md)
(merged as `44ec54e`) recommending `RFC-`, `kind: process`, `status: closed`, and surfaced one
thing it said was not the question. **RL-979 adopts the recommendation with one
disagreement. RL-980 places and settles the surfaced item**, which the lead asked be placed
rather than guessed at.

**The derivation is right about the thing that matters, and it found it by counting where
RL-978 did not.** RL-978 §3 item 3 named *"Plan review 9's two citations"* as a constraint.
There are **three**, and the third is the discriminator. Verified at `cc17404`,
`docs/closures/CR-00932-plan-review-11-completing-the-review-sequence-at-wk-671-s-close-before-wk-672-opens.md:174`, inside Plan review 11 (which opens at 2485):

> acceptance — correct, per the "Pending proposals" section's **own rule** that "numbering
> happens

Plan review 9's two citations are *provenance*. This one is **normative** — it quotes a rule the
container states and applies it to judge another record's conduct. **That is what separates the
two placements RL-978 left standing**, and it is invisible to RL-989 class 4, which the
derivation tested and found passes both.

## Authority

- **Routed by the lead** under the maintainer's delegation of 2026-09-01
  ([`RL-00940-the-maintainer-s-delegation-and-rfc-937-s-precedence-recorded-2026-09-01.md`](RL-00940-the-maintainer-s-delegation-and-rfc-937-s-precedence-recorded-2026-09-01.md)
  §1); neither ruling falls in its §2 exclusions.
- **RL-979 completes RL-978's hand-back** — the exclusion was ruled, the positive
  assignment derived, and it returns here. The RL-975 / 82 / 84 / 86 pattern.
- **RL-980 is placed as well as ruled, and the lead may strike it without touching 88.** The
  lead asked *"whether that is a ruling, a precondition for W37-5b, or a disclosure for the
  go-ahead package"*. My placement is **a ruling and a disclosure, not a W37-5b precondition** —
  reasoned in RL-980 §1 — and since the decision is small and the enumeration is already in
  hand, it is ruled here rather than routed back for a second round trip. That efficiency is
  the lead's to reject.
- **Every figure is measured at `cc17404`**, `origin/main`'s tip when this record was written
  and this branch's base.
- **No note, template or filed plan is edited.** RL-978 is amended in one constraint, and an
  amendment to a filed ruling is a new dated artifact — this one — never an edit to the old.

## Acceptance Standard

`audit-docs.py` check 28 requires this section on dated `docs/plans/` files outside four
suffixes while its own docstring disclaims that scope — register finding F68, whose discharge
RL-996 showed to be unsound. Honoured here; the check is not patched from this branch.

1. `git grep -n '^#\+ Ruling ' docs/plans/` shows 88–89 immediately after 87, no duplicate, no
   skip.
2. Each ruling names the chosen option and every rejected one. RL-979 adopts the
   derivation's §4 table by reference and states the single column where it disagrees.
3. Each acceptance is a violation that must become detectable.
4. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
5. `git diff --stat origin/main...docs/w37-rulings-88-89-container-family` names exactly this
   one new file.
6. Every count below was produced by the command shown, and the enumeration in RL-980 §1 is
   given in full rather than summarised, because summarising it is how its predecessor went
   wrong.

---

## RL-979 — the container is `RFC-`, `kind: process`, `status: closed`; `owner:` is the maintainer, not the planner

### 1. Verified first, at `cc17404`

| Claim | Result |
|---|---|
| Boundary is lines 1155–1232 | **Confirmed** — 1155 is `## Pending proposals …`, 1233 is `### Plan review 9 …` |
| A third citation exists, at 2645, inside Plan review 11 | **Confirmed** — quoted above; Plan review 11 opens at 2485 |
| The section-close trap | **Confirmed** — `grep -c '^##[^#]' docs/closures/INDEX.md#plan-reviewsmd` returns **1** |
| Nothing enforces `owner:` against §1.6's family table | **Confirmed** — `check_owner` (`scripts/audit-docs.py:1868`) tests membership of `_VALID_OWNERS` = `{maintainer}` ∪ role-file stems, and the per-directory allowlist has no populated source |

### 2. Ruled

**`RFC-`, `kind: process`, `status: closed`, `created: 2026-08-29`, `was:`
`docs/closures/INDEX.md#plan-reviewsmd`, as its own record — placement P1.**

The derivation's §4 table is adopted: it walks §1.2's *full* family table rather than a
shortlist, and `RFC` fits on every column — family (a proposal), unit (*"one topic"*: two rules
for one rule set), `kind: process` (the topic is process rules), mutability (frozen), and
`status: closed` on §1.2a's own vocabulary, which names **"promoted"** among the words `closed`
replaces. `superseded` is correctly rejected: §1.2a reserves it for replacement by a named
successor in `superseded_by:`, and no document replaces this one.

**P1 over P2, on the third citation.** Under P2 — the container as Plan review 9's preamble —
line 2645's *"the 'Pending proposals' section's own rule"* resolves to Plan review 9, **a record
that did not state that rule and whose own text records taking the candidates up rather than
writing them.** A migration that silently reattributes a normative rule from its author to a
later reader of it is worse than one that fails loudly. Class 4 passes both placements, exactly
as RL-978 anticipated; this is what discriminates.

**Disagreed: `owner: planner`.** The derivation recommends it. §1.6's `RFC` row reads
*"maintainer mints and owns; any role drafts on instruction; lead assesses"*. **`owner:` is
`maintainer`.** Three reasons:

1. **§1.6's column is "Owner — creates & amends", not "author".** It names who is responsible
   for the document, and it *explicitly contemplates a different drafter* — *"any role drafts on
   instruction"*. The planner's authorship is not erased by this; it is in the body and in
   `was:`.
2. **`owner: planner` would make this the only `RFC-` in the corpus whose owner contradicts
   §1.6**, and nothing would catch it — `check_owner` accepts any role name.
3. **The container's own text agrees.** *"The review at WK-671's close folds these in, numbers
   them, and takes them to the maintainer."* It is a proposal *to* the maintainer; the
   maintainer owns its disposition.

**Amended: RL-978 §3 item 3's fourth constraint.** It says *"Plan review 9's two
citations … must resolve after the rewrite."* **There are three, and the third is a different
species.** RL-978's conclusions are unaffected — the boundary, the `CR-` exclusion, the
no-widening rule and the two-placement finding all stand — but its constraint list was
incomplete, and the missing member is the one that decides between the two placements it left
open. Recorded as an amendment rather than a correction to the merged record, per the
immutability rule that record itself states.

**Rejected: every other family**, on the derivation's §4 grounds. The one worth restating is
`FD`: the container calls its own first observation *"the first finding"*, and it is still not a
`FD-`, because that observation was recorded and fixed upstream inside the section — there is no
open finding to carry a register row.

### 3. What it obliges

The derivation's six obligations are adopted. Three carry additions:

1. **The section closes at the next *record* heading, never at the next same-level heading.**
   The file has exactly one level-2 heading, so *"from the `##` to the next `##`"* yields 1155
   to end of file — swallowing Plan reviews 9, 10 and 11. **This is RL-978 §3 item 4's
   mis-nesting finding resurfacing as an implementation trap**, and it is why RL-978 fixed
   the boundary by line number rather than by rule.
2. **Three citations rewrite, not two**, and 2645's must keep its attribution to the container.
3. **`owner: maintainer`**, per §2.
4. **The phrase *"both above in this document"* at 2121 stops being true under either
   placement** and is replaced, not merely re-pointed. A citation that resolves and reads false
   satisfies RL-978's constraint and still misleads.
5. **The three `###` candidates stay body inside the `RFC-`**, satisfying the twelve-non-close
   derivation's standing acceptance item in both directions: none minted as a record, none
   dropped.

### 4. Acceptance — the violation that must become detectable

**The violation: a normative rule is attributed, after the migration, to a record that did not
state it.**

- **Line 2645's rewritten citation names the container's `RFC-` id**, not Plan review 9's `CR-`.
  *Violation: a normative citation whose target is the wrong record.* The positive control is
  placement P2, which produces exactly this and passes class 4.
- **A fixture whose only level-2 heading is followed by three record headings**, split by
  whatever implements §3 item 1. *Violation: a section that runs to end of file because its
  close was derived from heading level.* This must fail against any *"to the next `##`"* rule.
- **The container's `owner:` is not the role that drafted it**, and a check compares each
  migrated document's `owner:` against §1.6's row for its family. *Violation: an `owner:` that
  is valid but contradicts the family table* — which `check_owner` permits today.

---
