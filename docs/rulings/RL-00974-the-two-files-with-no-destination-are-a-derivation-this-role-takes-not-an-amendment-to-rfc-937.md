---
id: RL-974
family: ruling
title: the two files with no destination are a derivation this role takes, not an amendment to RFC-937
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

## RL-974 — the two files with no destination are a derivation this role takes, not an amendment to RFC-937

### 1. The question the lead asked, answered first

**It is a technical decision, and it is taken here.** RFC-937 §5.2 is an **impact map** — a
derived enumeration of what the migration must move — not a normative rule. §1 is the standard,
§2's D0-D14 are the decisions, and neither is touched by assigning a destination to a file §5.2's
hand-built table failed to enumerate. Both destinations follow from rules **already in the note**,
so this is applying §5.2's own logic to two rows it missed. RL-990 set the precedent and it is
this role's: *"Nothing in `docs/rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md` is edited."* Nothing is edited
here either.

Had either file required a rule the note does not contain — a new family, a new `kind:`, a change
to §1 — it would have gone to the maintainer. Neither does.

### 2. Verified

`docs/audit/` holds 43 tracked files. §5.2's eight `docs/audit/` rows cover 41 by exact name or
glob. The two uncovered are exactly the two the plan names:

- **`docs/research/RS-01002-rfc-937-verification-and-impact-sweep-audit-record.md`** — an auditor sweep record dated
  2026-09-02, filed after RFC-937 merged. It postdates the table that would have to list it,
  which is why no row reaches it.
- **`docs/findings/FD-00894-rfc-840-841-adoption-pilot.md`** — §5.2's work row is
  `audit/work/*/README.md`; this is a sibling non-README file in that same directory and falls
  outside the glob.

`git grep -in 'sweep\|pilot-findings\|nt-0010-0011-adoption' docs/rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md`
returns nothing, confirming neither is named anywhere in the note.

### 3. Ruled

**Both become `RS- kind: audit`, owner auditor**, under RFC-937 §1.2's `RS` `audit` row — *"a
bespoke audit's method, evidence and verdicts; files every finding as `FD-`"* — and D13's owner
assignment (*"research → executor, except `RS- kind: audit` → auditor"*).

- The sweep record: this is the plan's own proposal and it is correct. It is a bespoke audit's
  method, evidence and verdicts, and nothing else in the family set fits it.
- `pilot-findings.md`: it is the method, evidence and verdicts of the `CLAUDE.md` §15 step 6
  pilot run against the role charters — the same shape, produced by the same kind of exercise.
  Its sibling `README.md` becomes a `CR- kind: work` under §5.2's existing row, and §1.2's `RS`
  `audit` row already requires that `CR-` to cite the record, so the pair keeps its structure.

**Rejected: folding either into the `CR-` its neighbour becomes.** Acceptance (g) class 4
requires *"the concatenation of the outputs reproduces the input's body lines in order"*; folding
two documents into one moves body lines between outputs and is exactly what that class exists to
catch.

**Rejected: minting an `FD-` per numbered finding in either.** The `RS` `audit` row's *"files
every finding as `FD-`"* governs a bespoke audit **going forward**; applied retroactively it
would re-key `pilot-findings.md`'s P-numbered findings into a permanent id family, which is a
migration nobody planned and which §5.2 does not contemplate for any other record. **Apply the
whole rule prospectively and the narrow rule retrospectively**: a finding in either document that
is **still open** at the merge tree becomes an `FD-` and the `RS-` cites it; a finding the
document already records as resolved stays a section, and the `RS-` is filed at the status its
own content supports. *Half-applying this rule — the family without the findings clause — is the
failure mode, so the executor records which findings it found open and why.*

**A side finding for the executor, not a ruling.** §5.2's row for `audit/findings/F*.md`
annotates the count as `(5)`; the directory holds **11** `F*.md` files at `e93e0e4`. The row is a
glob, so coverage is unaffected and nothing is stranded — but the annotation has drifted, and a
count in a frozen note is not re-derivable by a later reader
([`RFC-756`](../rfcs/RFC-00756-duplicated-status-in-claude-md-goes-stale.md)). Do not inherit it.

### 4. Acceptance — the violation that must become detectable

1. **Every file must land somewhere, and the check already exists.** Acceptance item (a)'s zero
   `none` row over `docs/` catches an unclassified file. **Violation: a positive `none` row, or
   a classified total below `git ls-files docs/ | wc -l`.** Stated here so the executor knows (a)
   is the backstop for this class and does not add a second one.
2. **The two files must be findable afterwards.** **Violation:** `docs/REDIRECTS.csv` lacking a
   row whose source is `docs/research/RS-01002-rfc-937-verification-and-impact-sweep-audit-record.md` or
   `docs/findings/FD-00894-rfc-840-841-adoption-pilot.md`, or a row whose target does not
   exist. Named by path, because these two are precisely the files a glob-driven redirect
   generator will miss for the same reason §5.2 missed them.
3. **The findings clause must not be half-applied.** **Violation:** either document reaching the
   merge tree as an `RS- kind: audit` while a finding its own text marks open has no `FD-`.

---
