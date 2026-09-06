---
id: RL-980
family: ruling
title: a line-number citation into a split file is re-derived or replaced; a path-only rewrite is forbidden
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

## RL-980 — a line-number citation into a split file is re-derived or replaced; a path-only rewrite is forbidden

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
| `docs/closures/INDEX.md#plan-reviewsmd` (×3) | `:1994-1997`, `:1994-2006`, `:1979-1981` |
| `docs/findings/register.md` (×7) | `:2546-2554`, `:1979-1981` (×2 on one line), `:980-1000` (×2), `:2430` (×2) |
| `docs/plans/PL-00845-rfc-840-rfc-841-adoption-reconciliation-and-rulings-2026-08-29.md:102` | `plan-reviews.md:572` |
| `docs/plans/PL-00854-wk-671-scoring-sequenced-slice-plan.md:570` | `plan-reviews.md:774-791` |
| `docs/plans/PL-00930-wk-672-testing-map-plan.md:99` | `plan-reviews.md:2352` |
| `docs/closures/CR-00830-plan-review-8-at-wk-670-s-close.md:34` | `findings/register.md:26` |
| `docs/rulings/RL-00931-correct-the-example-do-not-build-the-breakdown.md` (×2) | `findings/register.md:92` |

**This is the third count of this class to come back wrong in one session**, after RL-985
§1(g)'s work rows and RL-995's token count — and the three have three different authors.
**The class is not one reader's carelessness**, which is the strongest available argument for
RL-985's census being derived rather than hand-counted. `git grep -c` counts *lines with
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
(`close-workstream/SKILL.md:646`), which puts it in RL-987's set as well, and an instrument
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
| **Whether `owner:` follows §1.6's family table or the historical author, in general** | RL-979 settles it for this document on that document's own facts. As a general rule it reaches every migrated document, and I have not enumerated the cases where the two diverge | **The planner**, as a derivation over the divergent cases, then back here. RL-995 §3 item 2 and RL-996 §3 item 2 are two more instances of the same question |
| **The heading mis-nesting in `plan-reviews.md`** | RL-978 §3 item 4 already made it the lead's | **The lead** — unchanged, and RL-979 §3 item 1 is why it now has an implementation cost as well as a rendering one |
| **Whether §5.2 gains a row for the container, or it is carried as a bespoke derivation** | Both are consistent; the derivation says so. A standard edit is the maintainer's, and the bespoke route needs no edit | **The lead**, at implementation. The bespoke route is available and cheaper |

## Provenance

Row 7, routed by the lead on 2026-09-02 with an instruction to read the record rather than the
summary, and with two corrections to RL-978 the lead had already checked. Both were verified
here independently. The `owner:` disagreement is mine and was not in either the derivation or
the routing brief; it was found by reading §1.6's row after the family was settled.
