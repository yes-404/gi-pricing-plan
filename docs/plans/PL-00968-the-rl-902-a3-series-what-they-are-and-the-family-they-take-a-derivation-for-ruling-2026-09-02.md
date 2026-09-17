---
id: PL-968
family: plan
kind: leaf
title: The `RL-902`–`A3` series: what they are, and the family they take — a derivation for ruling (2026-09-02)
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-09-02
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-09-02-w37-ruling-a-series-family-derivation.md
---

# The `RL-902`–`A3` series: what they are, and the family they take — a derivation for ruling (2026-09-02)

> **For agentic workers:** this is a derivation, not a plan and not a ruling. It enumerates
> an option set and recommends one. It binds nothing until the decision-maker rules on it.

**Goal:** answer RL-985's *Not ruled* row — *"What `RL-902`, `A2` and `A3` are"* — by
enumerating the option set under the identifier standard §1.2 and §1.7 and recommending one,
so the census that gates W37-5b can be cleared.

**Why this is the critical path.** RL-985 §3 item 1 puts its census before W37-6, and its
*Not ruled* row states the dependency in as many words: *"It is a RL-985 precondition: the
census cannot be cleared while three units are unclassified."*

**Spec:** [`../rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md`](../rfcs/RFC-00937-one-id-per-governed-thing-one-sequence-integer-identity-a-self-describing-layout-and-roles-per-family.md) §1.2
and §1.7.

**Tree:** every measurement below was produced by executing the shipped script or reading the
shipped source at **`b648c22`**. None is relayed. **Re-verified unchanged at `01bd0bd`**
(`main` after Rulings 79/80 landed in `e7e1d24`, which edits `scripts/doc-id.py`): both cited
line numbers still resolve to the same statements, and both discovery functions still return
what §2 records. The re-read is `delivery-process.md` §15 Rule 10's, and it is recorded rather
than asserted because the file this record cites by line number is one of the files that moved.

## Acceptance Standard

This derivation is complete when every item holds. Each is a violation that must be
detectable.

1. **The three headings are read, not inferred from their id form.** RL-985's routing says
   the id form is what surfaced them; it is not what decides them. *Violation: an option
   argued from the letter `A` alone, with no reading of what the three sections say.*
2. **The option set is enumerated before one is recommended**, each with its cost at the
   migration. *Violation: fewer than four options, or an option with no stated cost.*
3. **Every claim about what the code does today was produced by running it.** *Violation: any
   behavioural claim traceable only to reading. The test: re-run the command in its own
   paragraph at `b648c22` and reproduce the stated value.*
4. **The recommendation is handed over, not applied.** *Violation: this document changing any
   script, template or governed document, or reading as though the question were settled.*
5. **`python3 scripts/audit-docs.py` and `python3 scripts/req-coverage.py` both exit 0** on
   the branch carrying this file. *Violation: any non-zero exit.*

## Global Constraints

- **The decision is the decision-maker's** (`delivery-process.md` §3). A planner derives and
  recommends; it does not rule.
- **No filed plan is edited.** The 2026-08-30 adoption document is frozen at its date
  (`CLAUDE.md` §2); this record is about it, never in it.
- **Requirement ids and section numbers are permanent** (`CLAUDE.md` §5).

---

## 1. What the three actually are — read, not inferred

The three sit in
[`PL-00899-rfc-842-rfc-843-rfc-895-adoption-plan-delegation-and-rulings.md`](PL-00899-rfc-842-rfc-843-rfc-895-adoption-plan-delegation-and-rulings.md) at
lines 67, 81 and 96, under a `##` heading reading *"3. Rulings under the delegation"*.

**(a) They have the canonical ruling shape.** Each states a candidate, rejects it with a
reason, and then rules. A1: *"**Rejected, and the reason matters more than the choice** …
**Ruled: `.claude/skills/secret-hygiene`.**"* A2 and A3 are the same form. This is the
structure Rulings 66 to 84 use.

**(b) They were made under a dated, bounded delegation of the maintainer's own authority.**
The same document's §1.1 records it: *"authorise you to approve RFC-842 RFC-843 and RFC-895
landing on behalf of me"* — the maintainer, 2026-08-30 — read narrowly, covering *"the
landing of RFC-842, RFC-843 and RFC-895, and nothing else."*

**(c) They were implemented and independently verified as ruled.** The work record
`docs/closures/CR-00933-audit-record-nt-0012-0013-0014-adoption-docs-audit-checklists-work-item-close-md.md` carries slices C and D against commit
`97965be` (`#456`) and a section headed *"Rulings A1–A3, verified landed exactly as ruled"*,
each with the file and line where the ruled text now sits.

**(d) They are cited by name from other governed documents, as authorities.** Not only inside
their own file:

| Citing document | Line | How it cites |
|---|---|---|
| `docs/closures/CR-00933-audit-record-nt-0012-0013-0014-adoption-docs-audit-checklists-work-item-close-md.md` | 23, 88, 91, 94 | as the thing slices C and D implement, and as the subject of the verification |
| `docs/rulings/INDEX.md#2026-08-30-w11-reopen-hooks-and-bundle-resolution-rulingsmd` | 237 | *"which is the argument RL-903 already made"* — one ruling record citing another as precedent |

**A section of a plan does not get cited as precedent by a ruling record.** (d) is the single
strongest fact in this section.

**(e) The letter series was a deliberate choice, not an absence of the numbered one.** The
numbered sequence was in active use on the same day — ruling records dated 2026-08-30 carry
numbers up to 48 and 53:

```
for f in $(git ls-files docs/plans | grep 2026-08-30); do
  grep -oE '^#{1,3} Ruling [0-9]+' "$f" | grep -oE '[0-9]+$' | sort -n | tail -1
done
```

So the `A` marks something. Read against §1.1, the thing it marks is **authorship under the
delegation**: these are the lead's rulings under a bounded grant, not the decision-maker's
numbered series. That is a real semantic, and §2 weighs whether the identifier standard has
anywhere to put it.

---

## 2. What the code does with them today

Three measurements, each by execution.

**2.1 The splitter never sees them.** `_RULING_HEADING_RE` (`scripts/doc-id.py:1091`) is
`^##\s+Ruling\s+(\d+)\s*(?:—\s*(.+))?$`. The three headings fail it **twice over**: they are
`###` rather than `##`, and `A1` is not `(\d+)`. Running
`_RULING_HEADING_RE.findall(<the adoption file>)` returns **0** matches, so
`_discover_multi_ruling_files` hits its `if not headings: continue` and skips the file
entirely.

**2.2 The file therefore migrates as one plan.** Running `_discover_plain_plans` at `b648c22`
returns the adoption file as a single draft with prefix **`PL`** and `kind: leaf`. The three
rulings become body inside it. This is the status quo option, and it is what happens if
nobody decides anything.

**2.3 The citing tokens are invisible to the sweep as well.** `LEGACY_FORM_PATTERNS`'
ruling-reference alternative (`scripts/audit-docs.py`) is `\bRuling \d+\b`. It matches
`RL-987` and does **not** match `RL-902`. **21 `Ruling A<n>` tokens exist at
`b648c22` across five files, 15 of them outside the adoption document**, and acceptance item
(d)'s sweep returns none of them. Whatever is decided below, those 21 tokens are rewritten by
nothing and flagged by nothing.

---

## 3. The option set

Costed at the migration. §1.2 gives `RL` the unit **"one ruling"** and `PL` the unit
**"one plan"**; §1.7 states the standard's own model for a ruling that arrives after a plan is
frozen — *"they become sibling `RL-` records applied at a ledger step"*.

| # | Option | Cost at the migration | Assessment |
|---|---|---|---|
| **(a)** | **Three `RL-` records**, split out of §3, each `status: active`, `created: 2026-08-30`, `was:` the adoption file | Splitter must match `###` and a non-numeric ruling token; three ids from the global sequence; 21 token rewrites; three `REDIRECTS.csv` rows; the residual `PL-` keeps §1, §2, §4, §5 | **Recommended.** §1.2's unit is one ruling and there are three. §1.7's model is a sibling record. It is the only option under which (d)'s two external citations resolve to an id |
| **(b)** | **One `RL-`** carrying all of §3 | One id, one redirect; splitter still needs the `###` case | **Rejected.** §1.2 fixes `RL`'s unit as *one ruling*, bolded in the table. Three rulings in one record is the defect RL-975 rejected for closure records, in a different family |
| **(c)** | **Body inside the `PL-`** — the status quo of §2.2 | None; nothing changes | **Rejected, and it is the option that looks free.** §1.7's resolver is `\b(FR\|NFR\|DEP\|OQ\|WK\|SL\|WF\|ADR\|RFC\|PL\|LG\|RL\|RS\|CR\|FD)-0*(\d+)\b`; a section inside a plan has no id, so the work record and the WK-671 ruling record would cite something the standard cannot resolve. It also files three rulings under a family whose `kind:` vocabulary is `map · leaf · review · handover` — none of which is "ruling" |
| **(d)** | **Retroactively renumber** into the legacy sequence (`RL-997`–`87`), then split as normal | Two steps instead of one; a numbered token minted in 2026-09-02 for a 2026-08-30 decision | **Rejected.** It buys only the existing regex, and it invents history: the numbers would imply a sequence position these never held. The `was:` field already carries the old token, which is the mechanism for exactly this |
| **(e)** | **A declared exception** under RL-985's bucket 3 — named in code as deliberate non-records | One code entry with a reason string; census closes | **Rejected as the answer, available as a fallback.** It closes the arithmetic by asserting the three are not records, which (a) to (d) of §1 show to be false. RL-985 itself says a bucket-3 entry that could have been derived *"is a defect in the fix rather than in the corpus"* |

---

## 4. Recommendation, and what it would oblige

**Recommended: option (a) — three `RL-` records.**

The reasoning in one line: **§1.2's unit for `RL` is one ruling, three rulings exist, and two
governed documents already cite them as authorities.** Options (b) and (c) each break one of
those; (d) invents a sequence position; (e) records as false the thing §1 measured.

If ruled, it obliges:

1. **`_RULING_HEADING_RE` widens on two axes**, not one — heading level and token shape. The
   level fix alone leaves `A1` unmatched; the token fix alone leaves `###` unmatched. A fix
   that addresses one and reds nothing is the false-green case.
2. **`owner:` is not `decision-maker` for these three.** `scripts/doc-id.py:1150` hardcodes
   `owner="decision-maker"` for every split ruling. A1 to A3 were the **lead's**, under §1.1's
   delegation. Migrating them with a false owner would put a wrong attribution into a frozen
   record. This is a second obligation, and it is not visible from the family question.
3. **The 21 `Ruling A<n>` tokens are rewritten**, which requires §2.3's sweep gap closed
   first — otherwise acceptance item (d) passes while every one of them survives.
4. **Three `REDIRECTS.csv` rows**, one per new `RL-`, keyed on the old token rather than on a
   path, since three records come out of one file.
5. **The residual `PL-` is checked for sense.** After §3's three subsections leave, its §3
   heading is empty and its §4 acceptance table still cites *"Rulings A1–A3"*. RL-989
   acceptance (g) class 4 — body lines reproduced in order — is satisfiable, but a heading
   with nothing under it is a new defect the split creates.

---

## 5. Three things the measurement surfaced that are not this question

Recorded because §1's reading found them and they belong to somebody. **None is decided
here.**

**5.1 The three h1 ruling files migrate as plans, not rulings.** RL-985's *Not ruled*
routed to W37-6's executor the question of *"whether the splitter currently tries"* to split
them. Running both discovery functions at `b648c22` answers it: it does not try, and the
consequence is not the harmless one the routing anticipated. All three —
`../rulings/RL-00950-rl-949-3-point-2-s-fetch-path-is-broken-against-github-com-resolved-by.md`,
`../rulings/RL-00951-rl-947-s-tombstone-gains-per-file-stubs-watched-by-a-new-check-not-left.md` and
`../rulings/RL-00949-rfc-897-slice-2-s-census-csv-and-fr-72-the-test-is-overbroad-the.md` — come out of `_discover_plain_plans` as
**`PL-` with `kind: leaf`**. They are standalone ruling records, and they would migrate into
the plan family. *"One ruling per file and need no split"* is true and does not settle the
family.

**5.2 That falsifies F68's stated discharge.** The leaf plan §9 discharges F68 on the ground
that *"After the migration, `docs/plans/` holds only `PL-` files and rulings live in
`docs/rulings/` as `RL-` files."* Under §5.1 that premise is false for at least three files:
they are rulings and they would be `PL-`. F68's discharge condition needs re-testing against
what the splitter actually produces, not against the intended end state. The leaf plan
already says *"Prove that; do not assume it"* — this is the case it was guarding against.

**5.3 `Ruling A<n>` is a legacy form no pattern names.** §2.3. It is not the family question
and it does not go away under any option in §3, including doing nothing. It belongs with the
census, as the class of legacy token whose *shape* — not whose position — the sweep cannot
express. RL-985's second acceptance mutation asks for exactly this shape in a fixture;
this is the same shape in the real corpus.

---

## 6. What this derivation does not do

- It does not rule. The decision is the decision-maker's, and RL-978's precedent is the
  shape: the exclusion is ruled, the positive assignment is derived, the derivation comes back.
- It does not touch the frozen 2026-08-30 adoption document.
- It does not fix `_RULING_HEADING_RE`, the hardcoded owner, or the sweep gap. Each is named
  in §4 or §5 with its owner.
- It does not decide §5.1 or §5.2, which are a different question with a different owner and
  are filed here only because this measurement is what found them.
