---
id: RL-988
family: ruling
title: DP-2: the legacy-form sweep is repaired in two parts — fix the pattern first, then a bounded, load-bearing exclusion list
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-02
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-02-w37-migration-preconditions-rulings.md
---

## RL-988 — DP-2: the legacy-form sweep is repaired in two parts — fix the pattern first, then a bounded, load-bearing exclusion list

### 1. Verified first, at `04ec6bf`

| Claim | Verdict |
|---|---|
| §7 (d) *"is unpassable as written"* | **Confirmed, by the strongest available witness: the item matches its own text.** Running (d)'s pattern against line 426 of `docs/rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md` — the line that *is* §7 — returns one hit: `NT-00`, the bare prefix fragment inside (d)'s own alternation. After the migration that file is a frozen `RFC-` whose body lines the migration may not change (§4: *"Never changed: a body line of any frozen file"*), and `NT-00` with no following digits is not a citation the step-6 prefix allow-list can consume. The item fails on itself, permanently, with no defect anywhere in the migration |
| `REDIRECTS.csv` is among the *"structural hits"* the plan lists | **Loose, and it does not weaken the conclusion.** (d) already excludes `REDIRECTS.csv` and `was:` lines by name — those are the *"two"* exclusions option (a) proposes extending |
| *"(c) drops the code tree, which is where 767 of the citations live"* | **Not confirmed. The figure is a misreading, and the correct measurement is different and stronger.** 767 is RFC-937 §10's count of **files** — whole tree, all areas — matching the requirement-id pattern at `8f5d57d`; it is neither a code-tree share nor a count of citations. The same command returns **773 files** at `04ec6bf`, and `docs/roadmap.md`'s WK-697 row has already re-measured the in-scope figure to 768 at `bc7bc36`. Measured against (d)'s **own** pattern at `04ec6bf`: **881 files hit, of which 598 (68 %) lie outside `docs/`** — 496 of them code (`backend` 217, `frontend` 144, `packages` 135), plus `.claude` 55, `scripts` 16, `tests` 13, `examples` 6, `.github` 3, `deploy` 2 and seven root files |
| (d) and check 36 are the same rule | **Confirmed, and nothing in the plan connects them.** Check 36's third clause is *"no pre-migration form survives outside the CSV and `was:` lines"* — (d) at the migration tree, check 36 standing thereafter |

### 2. Ruled

**Chosen: option (a)** — a named constant exclusion list, extended from the two the item
already states, with a reason per entry — **in two parts, the first of which shrinks the list
the second has to carry.**

**Part 1 — fix the pattern; do not exclude the file.** Every alternative in (d) must match a
**complete** legacy identifier or path, never a proper prefix of one. `NT-00` is a prefix
fragment: it exists to catch `NT-00nn`, and written in the complete-id form it still catches
every note id that has ever existed while no longer matching its own text. The executor audits
every alternative against that rule, not only this one. **This is an amendment to the item's
pattern and is stated as one so it is visible** — a rule that yields still yields visibly.
Excluding a whole frozen file to hide a single fragment match would blind the sweep to every
genuine unrewritten citation in that same file, which is the opposite of what (d) is for.

**Part 2 — the residue, bounded.** What survives Part 1 is the class of file whose *function*
is to carry legacy forms as data. Exclusion is permitted for that class only, entry by entry:
`REDIRECTS.csv` (already in the item); `was:` lines wherever they appear (already in the item);
and a file whose purpose is to **name** legacy forms in order to detect or rewrite them —
`doc-id.py`'s rewrite pattern table, and the fixtures and expected-output files of the
migration and of check 36. Nothing else. In particular **no exclusion may name a path the
migration is required to rewrite**, which is what stops option (c) being smuggled back in one
entry at a time.

**Rejected: option (b), construct every pattern so it cannot self-match.** Not merely
unmaintainable — **insufficient**. The decisive self-match is `NT-00` inside RFC-937 §7's own
text: a body line of a file that after the migration is frozen and that §4 forbids the
migration to change. No amount of care in writing `doc-id.py` reaches it. The plan rejects (b)
for its cost; it should have rejected it for not working, and an implementer who reads only the
cost argument may revive (b) on the belief that a tidy encoding solves it.

**Rejected: option (c), narrow (d) to `docs/`.** It drops 598 of 881 files (68 %) at
`04ec6bf`, including all 496 code files, all of `.claude/`, `scripts/`, `tests/` and the root
governance files. That is a reduction in what the migration is *verified* to have done. It is
rejected on the merits — and see *What would have gone back to the maintainer* below, because
had it been the right answer it would not have been mine to give.

**One shared constant.** (d) and check 36 are one rule at two times, so they read **one**
constant in `scripts/audit-docs.py`, pattern and exclusion list defined once. Two definitions
of "a legacy form" will drift, which is `RFC-756`, and is exactly how the process-core extract
fell two commits behind its source with the gate green throughout (`CLAUDE.md` §15).

### 3. What it obliges

- W37-4 defines the constant alongside check 36 — the slice already carries a single
  module-level scoping constant for checks 30–39, so this is a second one beside it, not a new
  mechanism. **DP-2 therefore blocks W37-4, not only W37-6**; the plan marks it blocking on
  W37-6 alone, and that is the earlier of the two dates that matters.
- W37-5's fixture corpus proves the constant; W37-6's acceptance item (d) runs it.
- Each exclusion entry carries its reason inline, in the constant, not in a commit message.

### 4. Acceptance — the violation that must become detectable

1. **Every exclusion must be load-bearing.** Removing any single entry from the exclusion
   constant must make the sweep return at least one hit, and the hit must come from the file
   class that entry names. **Violation: an entry whose removal changes nothing** — it is
   unjustified and must be deleted. This is the check that keeps option (a) from decaying into
   option (c) by accretion.
2. **The sweep must still catch a real survivor.** Insert into a file that is **not** excluded
   one line per family carrying a complete legacy identifier — `RFC-897`, `FR-154`,
   `F-W9-3`, `F27`, `WF-698`, `RL-941`, `ADR-703`, `W11-3`, `docs/audit/`, `.claude/notes/`
   — and the sweep must return every one. **The positive control must invoke the shipped
   constant, never a re-typed copy of the pattern**: a control that runs a different regex body
   goes green because of what it misses. **Violation: any of the ten not returned.**
3. **One definition, not two.** Mutate the constant and both (d) and check 36 must change
   behaviour. **Violation: one changes and the other does not.**

---
