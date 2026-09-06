---
id: RL-909
family: ruling
title: Q1: the ride-ahead PR goes now, and its scope is wider than the note proposes; it is the auditor's, not an executor's
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

# RFC-896's five open questions, ruled (2026-08-30)

**What this is.** All five open questions in
[`../rfcs/RFC-00896-the-register-is-a-ledger-evidence-is-a-file.md`](../rfcs/RFC-00896-the-register-is-a-ledger-evidence-is-a-file.md)
§7, which that note marks *"(decision-maker, at reconcile)"* — step 2 of its own §6 adoption
sketch. Each arrived carrying a recommendation. **Three of the five recommendations are ruled
down** — one in its conclusion, two in their scope — because a note proposes and decides
nothing ([`../rfcs/README.md`](../rfcs/README.md)), and adopting a
proposal because it is the only text on the table is how an unexamined default becomes
governance.

**Numbering continues at 49, 50, 51, 52, 53.** Verified rather than relayed: every
`## Ruling N` heading under `docs/plans/` at `01ba0bd` (`origin/main`, fetched immediately
before this record was written) yields exactly 48 headings, numbered 1–48 with no gap and no
duplicate. 48 is
[`RL-00908-impact-matrix-row-4-does-not-sit-forever-it-inverts-and-part-c-row-5-closes-here.md`](RL-00908-impact-matrix-row-4-does-not-sit-forever-it-inverts-and-part-c-row-5-closes-here.md).

**Everything measured here was measured at `01ba0bd`**, at which `docs/findings/register.md` is
at `e9b5338` (2026-08-30, the F54 filing) and holds **51 data rows**. The register is amended
several times a day — 16 commits touched it on 2026-08-30 alone — so every count below is a
measurement at that revision and must be re-taken, not re-cited, when the adoption slices run.

**This record makes no edit to any other document.** `docs/findings/register.md`,
`.claude/skills/`, `.claude/roles/` and `docs/audit/checklists/` are all outside the
decision-maker charter's write scope. Every sentence these rulings oblige is specified
verbatim in §Text specified for others, at the end, and is written by the role named there.

---

## RL-909 — Q1: the ride-ahead PR goes now, and its scope is wider than the note proposes; it is the auditor's, not an executor's

### 1. Verified first, at `01ba0bd`

| Claim | Verdict |
|---|---|
| the register is amended frequently, not occasionally | **Confirmed** — 16 commits touched `docs/findings/register.md` on 2026-08-30 |
| findings are still being filed unowned | **Confirmed** — of the five rows filed 2026-08-30 (F50–F54), F50, F51, F52 and F54 all record an unowned or unassigned disposition |
| P1's premise, *"nothing new is invented; the header describes what the rows already do"* | **False for 10 of 51 rows** — see RL-910 §1 |
| the register header states rows are removed on resolution | **Confirmed, and contradicted by the corpus** — the header reads *"A finding is removed when the close resolves it, accepts it, or re-plans it with an owner"*, while 7 rows carry an in-place `Resolved <date>` annotation and remain: F-W10-1, F-W10-1-1, F-W10-2-1, F-W10-2-2, F32, F50, F51 |
| resolved rows are annotated in place, quoting what they supersede | **Confirmed** — F50's row ends `***Resolved 2026-08-30*** — … Closed by the auditor per this task's delegated authority` |
| a register row may be edited, unlike a filed plan | **Confirmed** — `docs/findings/register.md` has no do-not-edit rule; the in-place amendment convention is the register's normal operation. This is the fact RL-906 turned on, inverted |
| the auditor owns register rows | **Confirmed** — [`../../.claude/roles/auditor.md`](../../.claude/roles/auditor.md) §Owns: *"register deferral rows with named owners at `docs/findings/register.md`"* |

### 2. Ruled

**The ride-ahead PR goes now — Q1's recommendation is adopted in its conclusion.** But not
for the reason the note gives, and not at the scope it names.

The note's reason — *"every day of delay is another hand-parsed row"* — is a reason for P5,
not for P1. A header paragraph parses nothing. The register's own motivation item 3 says row
discipline is *"enforced by vigilance, not mechanism"*; a paragraph describing the grammar is
more vigilance. **P1 alone buys almost nothing on its own timescale.**

**P2 is what earns the ride-ahead.** Four of the five rows filed today are unowned. A decay
rule applied today puts them, and F7, F45, F46, F47 and F28's carried P5, on a named agenda
without any tooling existing. That value is real, immediate, and independent of P3, P4 and P5.

**The scope is widened, because RL-910 makes P1 the precondition of P3 being red on day
one.** The ride-ahead PR is therefore: the grammar paragraph (P1), the decay sentence (P2),
a named decay event on every unowned row (P2), **the correction of the header's false removal
sentence**, **conformance of the 10 non-conforming decision cells**, and **escaping of the
literal `|` characters in the F27 and F49 rows**, which split those rows into 7 and 6
table fields instead of 5.

**The header's removal sentence is corrected, not left standing.** `CLAUDE.md` §0: when two
records disagree, resolve it rather than quietly making either match the other. Here the
header and the rows disagree, seven times, and **the rows are right** — an in-place
`Resolved <date>` annotation citing the PR or SHA that discharged the finding is a better
record than a deletion, because a deleted row leaves a citation to it dangling and
`scripts/audit-docs.py`'s check 25 resolves finding citations against exactly this file. The
header moves. This matters beyond tidiness: check 25's own docstring quotes the removal
sentence as *"the register's own contract"* and builds a three-source fallback on it, so the
false sentence is already load-bearing in a gate.

**The writer is the auditor, not an executor.** Conforming a decision cell changes what a row
decides; that is `.claude/roles/auditor.md`'s owned artifact, and the two §13-verdict rows
(F53, F54) and the two negated-shape rows (F37, F40) each need a judgement no executor holds.

**P1 does not ride ahead without the conformance.** If the paragraph lands describing a
grammar 10 live rows do not follow, P3 must then either red on the live register or carry the
legacy exemption RL-910 rejects.

### 3. What it obliges

The auditor opens one docs PR against `docs/findings/register.md` with the six items above,
using the text in §Text specified for others. The lead merges it. If it lands, this note
files as the mechanism half only (P3–P5) and the adoption plan's S1 is deleted rather than
re-scoped.

**Overridden if** the PR lands the grammar paragraph without the conformance, if it deletes
any resolved row rather than annotating it, or if it is written by anyone other than the
auditor.

---
