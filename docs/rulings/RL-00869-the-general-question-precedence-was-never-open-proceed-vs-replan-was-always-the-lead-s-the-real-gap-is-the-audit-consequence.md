---
id: RL-869
family: ruling
title: the general question: precedence was never open; "proceed vs replan" was always the lead's; the real gap is the audit consequence
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-29
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-29-w11-ruling-vs-plan-scope.md
---

# When a merged ruling and a frozen plan's scope line collide, and R8 as applied in PR #400 (2026-08-29)

**What this is.** Two questions, raised by the lead against its own R8 (a lead ruling held
outside the repository, in a handover file, dated 2026-08-29 18:36Z). **RL-869** answers the
general question — which artifact governs, and who decides. **RL-870** ratifies or overturns
R8 as it was actually applied in PR #400, merged `39cb58e`.

**Numbering continues at 26.** Rulings 1–5, 6–13, 14–15, 16–21, 22 and 23–25 are the six earlier
records'; nothing here reuses a number ([`CLAUDE.md`](../../CLAUDE.md) §5).

**Mints no `FR-`/`NFR-`/`OQ-` id and no error code, and edits no specification.** Read against
`origin/main` at `39cb58e`, with `HEAD` identical.

**One thing this record deliberately does not do.** It does not amend
[`../process/delivery-process.md`](../process/delivery-process.md). The gap RL-869 finds is a
process obligation, and this role holds no grant over that file — the third instance of the
charter finding first filed as RL-878. It is proposed here and left for the planner to draft
and the maintainer to accept.

---

## RL-869 — the general question: precedence was never open; "proceed vs replan" was always the lead's; the real gap is the audit consequence

**The question as put.** *When a merged ruling and a frozen plan's scope line collide mid-slice,
which governs and who decides?*

**Ruled: the question contains three separable questions, two of which are already answered in
writing and one of which is genuinely missing. None of the three is a new precedence rule.**

### Part 1 — which governs is already decided, in `docs/plans/README.md`

RL-856's lesson applies to a governance question exactly as it applies to a specification one:
sweep before calling anything open. [`../plans/README.md`](../plans/README.md) in this directory already says it,
in three places:

- **"A filed plan is a record, not an instruction."** Its whole section under that heading: each
  file *"is frozen at its date. It says what was believed, intended and decided *then* — including
  the parts that later turned out to be wrong"*, and *"if a plan is wrong, the correction belongs
  in the document that is still authoritative."*
- **Convention 4** requires the opposite of deference to the plan: *"Re-check for rulings between
  the evidence sweep and the pull request — premises age faster than literals … a decision-maker is
  ruling concurrently and a ruling is not a commit to the tree your sweep pinned."* Its worked
  example is this very slice — six rulings landing in one hour, one of which *"corrected a defect
  the plan would otherwise have shipped."*
- **Convention 5**: *"Apply a ruling at every site it operates, not only where the plan discusses
  it."*

So **the later ruling governs**, and R8's holding restates existing doctrine rather than making
new law. That is worth saying plainly, because it changes what the lead's error was: R8 did not
invent a precedence rule in a domain that belonged to someone else. It applied one that was
already written down.

### Part 2 — who decides splits three ways, and only one part was ever this role's

| Question | Whose | Authority |
|---|---|---|
| Does the ruling govern the plan's scope line? | **Nobody's — already decided** | `docs/plans/README.md`, conventions 4 and 5 |
| Can this ruling be discharged inside this plan's scope at all? | **The decision-maker's** | It is a statement about what the ruling requires, so it belongs to the ruling's author |
| Proceed on the widened touch-set, or replan the slice? | **The lead's, explicitly** | [`../process/delivery-process.md`](../process/delivery-process.md) §3: the Lead *"reviews plan resolutions and decides replan vs. proceed"* |

**So R8's operative half was in charter.** "Proceed rather than split a two-line exemption into a
second process-slice" is a replan-vs-proceed call, and §3 assigns that to the lead in terms. What
R8 did *not* do was ask the middle question before answering the third — it inferred that Ruling
22 could not be honoured inside Task 1.2's scope, correctly, rather than asking. The correct
sequence was **one round trip, not a different decision**, and the record should say so rather
than book a larger error than occurred. The lead's own framing — *"my error to route rather than
rule"* — is more severe than the facts support in one direction and misses the gap in the other.

### Part 3 — the gap that is real, and it is not about precedence

Conventions 4 and 5 are about **literals and premises** ageing — a signature, an enum member, a
fixture name, a measured figure. A **scope line** is different in kind: it is not a fact that can
be wrong, it is a boundary the auditor audits against. Two things follow that nothing currently
says:

1. **Nothing requires anyone to tell the auditor.** R8's most useful sentence is its own:
   *"The auditor must be told this explicitly, or it will correctly flag `compile.py` in the diff
   as a scope violation against the plan it audits from."* That is true, it was handled by hand
   this time, and the process does not require it. An auditor reading a frozen plan and a diff
   has no way to distinguish a ruling-driven widening from drift — and §3's own role table
   charges the auditor with *"fresh context (no memory of implementation reasoning)"*, which is
   exactly the condition under which the distinction is invisible. (That phrase is the process
   document's, **not** `.claude/roles/auditor.md`'s, which carries no context clause at all — a
   gap worth noting separately, since the charter is what the role is spawned from.)
2. **A widened touch-set leaves no artifact.** `CLAUDE.md` §12 requires every decision to land as
   a dated artifact, *"never in chat"*. R8 is in a handover file outside the repository, which
   `docs/plans/README.md` describes as the class that *"dies with its session"* — the same
   objection §15 makes to an inline brief.

**Proposed, not written** (see the note at the head of this record): an obligation in
`docs/process/delivery-process.md` §11 or §12 that when a ruling widens a slice's touch-set
beyond its frozen plan, the PR description names the ruling, the file it forces, and the plan
line it exceeds — and the audit record notes it as ruling-driven rather than as drift. PR #400
in fact did all of this in its own description; the proposal is only to require what this
instance already did well, which is the cheapest kind of process change to accept.

**Acceptance test — the violation that must become expressible.** Today "this diff exceeded its
plan's scope, and no artifact in the repository says why" cannot be checked, because the *why*
lives in a handover file. After the proposed obligation, the expressible violation is a merged PR
whose diff touches a file its plan scopes out with no ruling named in the description and no note
in the audit record. **This ruling is overridden** if a later record treats a frozen plan's scope
line as binding over a merged ruling — the precedence is `docs/plans/README.md`'s, not this
record's, and a contrary holding would need to amend that file rather than cite a newer ruling.

---
