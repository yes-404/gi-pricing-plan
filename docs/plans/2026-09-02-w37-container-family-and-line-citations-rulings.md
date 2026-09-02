# The `Pending proposals` container's family, and line-number citations into a split file, ruled (2026-09-02)

**What this is.** Register row 7. The planner returned
[`2026-09-02-w37-pending-proposals-container-family-derivation.md`](2026-09-02-w37-pending-proposals-container-family-derivation.md)
(merged as `44ec54e`) recommending `RFC-`, `kind: process`, `status: closed`, and surfaced one
thing it said was not the question. **Ruling 88 adopts the recommendation with one
disagreement. Ruling 89 places and settles the surfaced item**, which the lead asked be placed
rather than guessed at.

**The derivation is right about the thing that matters, and it found it by counting where
Ruling 82 did not.** Ruling 82 §3 item 3 named *"Plan review 9's two citations"* as a constraint.
There are **three**, and the third is the discriminator. Verified at `cc17404`,
`docs/audit/plan-reviews.md:2645`, inside Plan review 11 (which opens at 2485):

> acceptance — correct, per the "Pending proposals" section's **own rule** that "numbering
> happens

Plan review 9's two citations are *provenance*. This one is **normative** — it quotes a rule the
container states and applies it to judge another record's conduct. **That is what separates the
two placements Ruling 82 left standing**, and it is invisible to Ruling 68 class 4, which the
derivation tested and found passes both.

## Authority

- **Routed by the lead** under the maintainer's delegation of 2026-09-01
  ([`2026-09-01-maintainer-delegation-and-nt-0019-precedence.md`](2026-09-01-maintainer-delegation-and-nt-0019-precedence.md)
  §1); neither ruling falls in its §2 exclusions.
- **Ruling 88 completes Ruling 82's hand-back** — the exclusion was ruled, the positive
  assignment derived, and it returns here. The Ruling 78 / 82 / 84 / 86 pattern.
- **Ruling 89 is placed as well as ruled, and the lead may strike it without touching 88.** The
  lead asked *"whether that is a ruling, a precondition for W37-5b, or a disclosure for the
  go-ahead package"*. My placement is **a ruling and a disclosure, not a W37-5b precondition** —
  reasoned in Ruling 89 §1 — and since the decision is small and the enumeration is already in
  hand, it is ruled here rather than routed back for a second round trip. That efficiency is
  the lead's to reject.
- **Every figure is measured at `cc17404`**, `origin/main`'s tip when this record was written
  and this branch's base.
- **No note, template or filed plan is edited.** Ruling 82 is amended in one constraint, and an
  amendment to a filed ruling is a new dated artifact — this one — never an edit to the old.

## Acceptance Standard

`audit-docs.py` check 28 requires this section on dated `docs/plans/` files outside four
suffixes while its own docstring disclaims that scope — register finding F68, whose discharge
Ruling 87 showed to be unsound. Honoured here; the check is not patched from this branch.

1. `git grep -n '^#\+ Ruling ' docs/plans/` shows 88–89 immediately after 87, no duplicate, no
   skip.
2. Each ruling names the chosen option and every rejected one. Ruling 88 adopts the
   derivation's §4 table by reference and states the single column where it disagrees.
3. Each acceptance is a violation that must become detectable.
4. `python3 scripts/audit-docs.py` exits 0 on the branch carrying this record.
5. `git diff --stat origin/main...docs/w37-rulings-88-89-container-family` names exactly this
   one new file.
6. Every count below was produced by the command shown, and the enumeration in Ruling 89 §1 is
   given in full rather than summarised, because summarising it is how its predecessor went
   wrong.

---

## Ruling 88 — the container is `RFC-`, `kind: process`, `status: closed`; `owner:` is the maintainer, not the planner

### 1. Verified first, at `cc17404`

| Claim | Result |
|---|---|
| Boundary is lines 1155–1232 | **Confirmed** — 1155 is `## Pending proposals …`, 1233 is `### Plan review 9 …` |
| A third citation exists, at 2645, inside Plan review 11 | **Confirmed** — quoted above; Plan review 11 opens at 2485 |
| The section-close trap | **Confirmed** — `grep -c '^##[^#]' docs/audit/plan-reviews.md` returns **1** |
| Nothing enforces `owner:` against §1.6's family table | **Confirmed** — `check_owner` (`scripts/audit-docs.py:1868`) tests membership of `_VALID_OWNERS` = `{maintainer}` ∪ role-file stems, and the per-directory allowlist has no populated source |

### 2. Ruled

**`RFC-`, `kind: process`, `status: closed`, `created: 2026-08-29`, `was:`
`docs/audit/plan-reviews.md`, as its own record — placement P1.**

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
as Ruling 82 anticipated; this is what discriminates.

**Disagreed: `owner: planner`.** The derivation recommends it. §1.6's `RFC` row reads
*"maintainer mints and owns; any role drafts on instruction; lead assesses"*. **`owner:` is
`maintainer`.** Three reasons:

1. **§1.6's column is "Owner — creates & amends", not "author".** It names who is responsible
   for the document, and it *explicitly contemplates a different drafter* — *"any role drafts on
   instruction"*. The planner's authorship is not erased by this; it is in the body and in
   `was:`.
2. **`owner: planner` would make this the only `RFC-` in the corpus whose owner contradicts
   §1.6**, and nothing would catch it — `check_owner` accepts any role name.
3. **The container's own text agrees.** *"The review at W11's close folds these in, numbers
   them, and takes them to the maintainer."* It is a proposal *to* the maintainer; the
   maintainer owns its disposition.

**Amended: Ruling 82 §3 item 3's fourth constraint.** It says *"Plan review 9's two
citations … must resolve after the rewrite."* **There are three, and the third is a different
species.** Ruling 82's conclusions are unaffected — the boundary, the `CR-` exclusion, the
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
   to end of file — swallowing Plan reviews 9, 10 and 11. **This is Ruling 82 §3 item 4's
   mis-nesting finding resurfacing as an implementation trap**, and it is why Ruling 82 fixed
   the boundary by line number rather than by rule.
2. **Three citations rewrite, not two**, and 2645's must keep its attribution to the container.
3. **`owner: maintainer`**, per §2.
4. **The phrase *"both above in this document"* at 2121 stops being true under either
   placement** and is replaced, not merely re-pointed. A citation that resolves and reads false
   satisfies Ruling 82's constraint and still misleads.
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

## Ruling 89 — a line-number citation into a split file is re-derived or replaced; a path-only rewrite is forbidden

### 1. Placed first, because the lead asked for a placement

**It is a ruling and a disclosure. It is not a W37-5b precondition.**

- **Not a precondition**, because W37-5b carries pre-run checks and this is an obligation on
  §4 step 6, the citation rewrite — it is discharged *during* the run, not before it.
- **A ruling**, because *"rewrite every citation"* does not say what rewriting a citation with
  an offset into it means, and the two available answers differ. Nothing in the standard settles
  it.
- **A disclosure**, because the failure is silent: the citation resolves and points at the wrong
  place, which no gate catches. §4.4's *"what becomes irreversible"* is where that belongs.

### 2. Verified first, at `cc17404` — the enumeration in full

The derivation reports *"fourteen line-number citations … 11 into `plan-reviews.md`, 3 into
`register.md`"*. Measured:

```
$ git grep -oE 'plan-reviews\.md:[0-9]+' | wc -l        → 14
$ git grep -oE 'audit/register\.md:[0-9]+' | wc -l      →  3
```

**Seventeen, across seven citing files** — the derivation's *"fourteen"* is the
`plan-reviews.md` count alone, and its 11 undercounts by three. All seventeen:

| Citing file | Citation |
|---|---|
| `.claude/skills/close-workstream/SKILL.md:646` | `plan-reviews.md:987-1005` |
| `docs/audit/plan-reviews.md` (×3) | `:1994-1997`, `:1994-2006`, `:1979-1981` |
| `docs/audit/register.md` (×7) | `:2546-2554`, `:1979-1981` (×2 on one line), `:980-1000` (×2), `:2430` (×2) |
| `docs/plans/2026-08-29-nt-0010-0011-reconciliation-rulings.md:102` | `plan-reviews.md:572` |
| `docs/plans/2026-08-29-w11-scoring.md:570` | `plan-reviews.md:774-791` |
| `docs/plans/2026-08-31-w12-map-plan.md:99` | `plan-reviews.md:2352` |
| `docs/audit/plan-reviews.md:788` | `audit/register.md:26` |
| `docs/plans/2026-08-31-f62-timing-ms-ruling.md` (×2) | `audit/register.md:92` |

**This is the third count of this class to come back wrong in one session**, after Ruling 83
§1(g)'s work rows and Ruling 86's token count — and the three have three different authors.
**The class is not one reader's carelessness**, which is the strongest available argument for
Ruling 83's census being derived rather than hand-counted. `git grep -c` counts *lines with
matches*, not matches, and two of the seventeen share a line.

### 3. Ruled

**A citation carrying a line offset into a file the migration splits is either (a) re-derived
into the destination record's own numbering, or (b) replaced by a form that needs no offset — the
destination record's id, with a quoted phrase or heading where precision is wanted. A rewrite
that changes only the path is forbidden.**

**Why a path-only rewrite is the wrong default even though it is what step 6 does.** Line 1994
of a 2816-line file is not line 1994 of the ~920-line record it lands in. The rewritten citation
**resolves** — to a real file — and points somewhere unrelated. The sweep detects these (the
`docs/audit/` prefix matches), so they are not invisible to acceptance item (d); what (d) cannot
see is whether the *number* was carried across correctly. **Detection is not repair**, and a
citation that is wrong while resolving is worse than one that fails loudly.

**(a) and (b) are both permitted, and which applies is per-citation.** Re-derivation is viable
here precisely because the destination records are frozen, so their line numbers are stable —
that is not true in general and is the reason (b) is preferred where the citation is to a *rule*
rather than to a passage. **One of the seventeen is inside an instrument**
(`close-workstream/SKILL.md:646`), which puts it in Ruling 66's set as well, and an instrument
should not teach an offset citation into a governed record: **that one takes (b).**

**Rejected: leaving them, on the ground that the sweep detects them.** §2 shows detection
without repair. **Rejected: dropping every line number.** It is lossy where the citation points
into a long record and the point is a passage, not a rule.

### 4. Acceptance — the violation that must become detectable

**The violation: after the migration, a citation names a destination record and a line number
that was not re-derived inside it.**

- **A check that no citation matches `<any pre-migration path>:<digits>`.** *Violation: a
  surviving legacy path with an offset.* Must fail today, naming all seventeen — the corpus is
  the positive control.
- **The ledger records, per citation, its destination record and whether it took (a) or (b).**
  Seventeen rows. *Violation: a citation rewritten with no recorded disposition* — which is the
  only way to tell a re-derived number from a carried-over one, since both are digits.
- **`close-workstream/SKILL.md:646` carries no line offset after the migration.** *Violation: an
  instrument teaching an offset citation into a governed record.*

---

## Not ruled — and where each goes

| Item | Why not mine | Where it goes |
|---|---|---|
| **Whether `owner:` follows §1.6's family table or the historical author, in general** | Ruling 88 settles it for this document on that document's own facts. As a general rule it reaches every migrated document, and I have not enumerated the cases where the two diverge | **The planner**, as a derivation over the divergent cases, then back here. Ruling 86 §3 item 2 and Ruling 87 §3 item 2 are two more instances of the same question |
| **The heading mis-nesting in `plan-reviews.md`** | Ruling 82 §3 item 4 already made it the lead's | **The lead** — unchanged, and Ruling 88 §3 item 1 is why it now has an implementation cost as well as a rendering one |
| **Whether §5.2 gains a row for the container, or it is carried as a bespoke derivation** | Both are consistent; the derivation says so. A standard edit is the maintainer's, and the bespoke route needs no edit | **The lead**, at implementation. The bespoke route is available and cheaper |

## Provenance

Row 7, routed by the lead on 2026-09-02 with an instruction to read the record rather than the
summary, and with two corrections to Ruling 82 the lead had already checked. Both were verified
here independently. The `owner:` disagreement is mine and was not in either the derivation or
the routing brief; it was found by reading §1.6's row after the family was settled.
